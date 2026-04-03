"""
Israel Central Bureau of Statistics (CBS) API Interface

This module provides functions to access time series data from Israel's CBS API.
"""

import requests
import pandas as pd
import xml.etree.ElementTree as ET
from typing import Optional, Union
import warnings




def il_cbs_api(
    series_id: Union[str, int],
    startPeriod: Optional[str] = None,
    endPeriod: Optional[str] = None,
    format_type: str = "json",
    download: bool = False,
    lang: str = "en"
) -> pd.DataFrame:
    """
    Fetch time series data and metadata from Israel's Central Bureau of Statistics API.
    
    Parameters:
    -----------
    series_id : str or int
        The CBS series ID (e.g., '3763', 3763, or '62902,62916' for multiple series)
    startPeriod : str, optional
        Start period in YYYY-MM format (e.g., '2020-01'). If None, retrieves full time series.
    endPeriod : str, optional  
        End period in YYYY-MM format (e.g., '2024-12'). If None, retrieves full time series.
    format_type : str, default 'json'
        Response format - 'json' or 'xml' (json is recommended)
    download : bool, default False
        Whether to download data (True) or just fetch (False)
    lang : str, default 'en'
        Language - 'en' for English, 'he' for Hebrew
        
    Returns:
    --------
    pd.DataFrame
        Time series data with TimePeriod, Value, series_id, and series_name columns.
        Metadata is accessible via the .meta attribute (e.g., data_df.meta)
        
    Example:
    --------
    >>> # Single series
    >>> data_df = il_cbs_api(3763, startPeriod='2023-01', endPeriod='2024-12')
    >>> print(data_df.head())
    >>> print(data_df.meta)  # Access metadata
    >>> 
    >>> # Multiple series
    >>> data_df = il_cbs_api('62902,62916')
    >>> print(data_df.meta)  # Metadata for all series
    >>> 
    >>> # Full time series (no date parameters)
    >>> data_df = il_cbs_api(3763)
    """
    
    # Convert series_id to string for API, preserving commas and text
    series_id_str = str(series_id)
    
    # Validate format_type
    if format_type.lower() not in ['json', 'xml']:
        raise ValueError("format_type must be 'json' or 'xml'")
    
    # Validate language
    if lang.lower() not in ['en', 'he']:
        raise ValueError("lang must be 'en' or 'he'")
    
    # Base URL and parameters
    base_url = "https://apis.cbs.gov.il/series/data/list"
    
    # Common parameters - only include non-None optional parameters
    base_params = {
        'id': series_id_str,
        'format': 'json',  # Force JSON format for consistent processing
        'download': str(download).lower(),
        'lang': lang.lower()
    }
    
    # Add optional time period parameters only if specified
    if startPeriod is not None:
        base_params['startPeriod'] = startPeriod
    if endPeriod is not None:
        base_params['endPeriod'] = endPeriod
    
    try:
        # Fetch data (data_hide=false)
        data_params = base_params.copy()
        data_params['data_hide'] = 'false'
        
        data_response = requests.get(base_url, params=data_params)
        data_response.raise_for_status()
        
        # Fetch metadata (data_hide=true)
        meta_params = base_params.copy()
        meta_params['data_hide'] = 'true'
        
        meta_response = requests.get(base_url, params=meta_params)
        meta_response.raise_for_status()
        
        # Process responses - always use JSON processing since we force JSON format
        data_df = _process_json_data(data_response.json())
        meta_df = _process_json_metadata(meta_response.json())
        
        # Attach metadata to the DataFrame using object.__setattr__ to avoid warnings
        object.__setattr__(data_df, 'meta', meta_df)
        
        return data_df
        
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch data from CBS API: {e}")
    except Exception as e:
        raise RuntimeError(f"Error processing CBS API response: {e}")


def _process_json_data(json_response: dict) -> pd.DataFrame:
    """Process JSON response to extract time series data."""
    try:
        all_series = json_response['DataSet']['Series']
        
        # Handle both single and multiple series
        all_data = []
        for series in all_series:
            observations = series.get('obs', [])
            series_id = series.get('id', '')
            series_name = series.get('path', {}).get('name_id', {}).get('name', '')
            
            # Handle case where observations is None (CBS API issue with mixed frequencies)
            if observations is None:
                observations = []
            
            # Extract time series data for this series
            for obs in observations:
                all_data.append({
                    'TimePeriod': obs['TimePeriod'],
                    'Value': obs['Value'],
                    'series_id': str(series_id),
                    'series_name': series_name
                })
        
        df = pd.DataFrame(all_data)
        
        # Handle empty results
        if df.empty:
            # Create empty DataFrame with expected structure
            df = pd.DataFrame(columns=['TimePeriod', 'Value', 'series_id', 'series_name'])
        else:
            # Convert TimePeriod to datetime if possible
            try:
                df['TimePeriod'] = pd.to_datetime(df['TimePeriod'])
            except:
                # Keep as string if conversion fails
                pass
            
            # Sort by time period and series_id
            df = df.sort_values(['series_id', 'TimePeriod']).reset_index(drop=True)
        
        return df
        
    except KeyError as e:
        raise ValueError(f"Unexpected JSON structure: missing key {e}")


def _process_json_metadata(json_response: dict) -> pd.DataFrame:
    """Process JSON response to extract metadata."""
    try:
        all_series = json_response['DataSet']['Series']
        
        # Handle both single and multiple series metadata
        all_metadata = []
        for series in all_series:
            metadata = {
                'id': series.get('id'),
                'time_unit': series.get('time', {}).get('name', ''),
                'data_type': series.get('data', {}).get('name', ''),
                'unit': series.get('unit', {}).get('name', ''),
                'precision': series.get('precis', ''),
                'last_update': series.get('update', ''),
                'level1': series.get('path', {}).get('level1', {}).get('name', ''),
                'level2': series.get('path', {}).get('level2', {}).get('name', ''),
                'level3': series.get('path', {}).get('level3', {}).get('name', ''),
                'level4': series.get('path', {}).get('level4', {}).get('name', ''),
                'series_name': series.get('path', {}).get('name_id', {}).get('name', '')
            }
            all_metadata.append(metadata)
        
        # Create DataFrame from metadata
        meta_df = pd.DataFrame(all_metadata)
        
        return meta_df
        
    except KeyError as e:
        raise ValueError(f"Unexpected JSON structure in metadata: missing key {e}")


def _process_xml_data(xml_text: str) -> pd.DataFrame:
    """Process XML response to extract time series data."""
    try:
        root = ET.fromstring(xml_text)
        
        # Find observations
        observations = []
        for obs in root.findall('.//obs'):
            time_period = obs.find('TimePeriod')
            value = obs.find('Value')
            
            if time_period is not None and value is not None:
                observations.append({
                    'TimePeriod': time_period.text,
                    'Value': float(value.text) if value.text else None
                })
        
        df = pd.DataFrame(observations)
        
        # Convert TimePeriod to datetime if possible
        if not df.empty:
            try:
                df['TimePeriod'] = pd.to_datetime(df['TimePeriod'])
            except:
                pass
            
            # Sort by time period
            df = df.sort_values('TimePeriod').reset_index(drop=True)
        
        return df
        
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse XML response: {e}")


def _process_xml_metadata(xml_text: str) -> pd.DataFrame:
    """Process XML response to extract metadata."""
    try:
        root = ET.fromstring(xml_text)
        
        # Find series element
        series = root.find('.//Series')
        if series is None:
            raise ValueError("No Series element found in XML")
        
        # Extract metadata
        metadata = {
            'id': _get_xml_text(series, 'id'),
            'time_unit': _get_xml_text(series, 'time/name'),
            'data_type': _get_xml_text(series, 'data/name'),
            'unit': _get_xml_text(series, 'unit/name'),
            'precision': _get_xml_text(series, 'precis'),
            'last_update': _get_xml_text(series, 'update'),
            'level1': _get_xml_text(series, 'path/level1/name'),
            'level2': _get_xml_text(series, 'path/level2/name'),
            'level3': _get_xml_text(series, 'path/level3/name'),
            'level4': _get_xml_text(series, 'path/level4/name'),
            'series_name': _get_xml_text(series, 'path/name_id/name')
        }
        
        # Create DataFrame from metadata
        meta_df = pd.DataFrame([metadata])
        
        return meta_df
        
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse XML metadata: {e}")


def _get_xml_text(element: ET.Element, path: str) -> str:
    """Helper function to safely extract text from XML element."""
    try:
        found = element.find(path)
        return found.text if found is not None else ''
    except:
        return ''


# For backward compatibility - now returns tuple for those expecting the old format
def il_cbs_api_legacy(series_id: Union[str, int], **kwargs) -> tuple:
    """
    Legacy version that returns tuple of (data_df, meta_df) for backward compatibility.
    
    Parameters same as il_cbs_api, returns tuple of (data DataFrame, metadata DataFrame).
    """
    data_df = il_cbs_api(series_id, **kwargs)
    return data_df, data_df.meta