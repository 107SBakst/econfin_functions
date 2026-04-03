"""
Israel Central Bureau of Statistics (CBS) API Interface

This module provides functions to access time series data from Israel's CBS API.
"""

import requests
import pandas as pd
import xml.etree.ElementTree as ET
from typing import Optional, Union, Tuple
import warnings


def il_cbs_api(
    series_id: Union[str, int],
    startPeriod: Optional[str] = None,
    endPeriod: Optional[str] = None,
    format_type: str = "json",
    download: bool = False,
    lang: str = "en"
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fetch time series data and metadata from Israel's Central Bureau of Statistics API.
    
    Parameters:
    -----------
    series_id : str or int
        The CBS series ID (e.g., '3763' or 3763)
    startPeriod : str, optional
        Start period in YYYY-MM format (e.g., '2020-01')
    endPeriod : str, optional  
        End period in YYYY-MM format (e.g., '2024-12')
    format_type : str, default 'json'
        Response format - 'json' or 'xml'
    download : bool, default False
        Whether to download data (True) or just fetch (False)
    lang : str, default 'en'
        Language - 'en' for English, 'he' for Hebrew
        
    Returns:
    --------
    tuple of (pd.DataFrame, pd.DataFrame)
        - First DataFrame: Time series data with TimePeriod and Value columns
        - Second DataFrame: Metadata about the series with .meta suffix in name
        
    Example:
    --------
    >>> data_df, meta_df = il_cbs_api(3763, startPeriod='2023-01', endPeriod='2024-12')
    >>> print(data_df.head())
    >>> print(meta_df.head())
    """
    
    # Convert series_id to string for API
    series_id_str = str(series_id)
    
    # Validate format_type
    if format_type.lower() not in ['json', 'xml']:
        raise ValueError("format_type must be 'json' or 'xml'")
    
    # Validate language
    if lang.lower() not in ['en', 'he']:
        raise ValueError("lang must be 'en' or 'he'")
    
    # Base URL and parameters
    base_url = "https://apis.cbs.gov.il/series/data/list"
    
    # Common parameters
    base_params = {
        'id': series_id_str,
        'format': format_type.lower(),
        'download': str(download).lower(),
        'lang': lang.lower()
    }
    
    # Add optional time period parameters
    if startPeriod:
        base_params['startPeriod'] = startPeriod
    if endPeriod:
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
        
        # Process responses based on format
        if format_type.lower() == 'json':
            data_df = _process_json_data(data_response.json())
            meta_df = _process_json_metadata(meta_response.json())
        else:  # xml
            data_df = _process_xml_data(data_response.text)
            meta_df = _process_xml_metadata(meta_response.text)
        
        # Add series_id for reference
        data_df['series_id'] = series_id_str
        meta_df['series_id'] = series_id_str
        
        return data_df, meta_df
        
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to fetch data from CBS API: {e}")
    except Exception as e:
        raise RuntimeError(f"Error processing CBS API response: {e}")


def _process_json_data(json_response: dict) -> pd.DataFrame:
    """Process JSON response to extract time series data."""
    try:
        series = json_response['DataSet']['Series'][0]
        observations = series.get('obs', [])
        
        # Extract time series data
        data_list = []
        for obs in observations:
            data_list.append({
                'TimePeriod': obs['TimePeriod'],
                'Value': obs['Value']
            })
        
        df = pd.DataFrame(data_list)
        
        # Convert TimePeriod to datetime if possible
        if not df.empty:
            try:
                df['TimePeriod'] = pd.to_datetime(df['TimePeriod'])
            except:
                # Keep as string if conversion fails
                pass
            
            # Sort by time period
            df = df.sort_values('TimePeriod').reset_index(drop=True)
        
        return df
        
    except KeyError as e:
        raise ValueError(f"Unexpected JSON structure: missing key {e}")


def _process_json_metadata(json_response: dict) -> pd.DataFrame:
    """Process JSON response to extract metadata."""
    try:
        series = json_response['DataSet']['Series'][0]
        
        # Extract metadata
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
        
        # Create DataFrame from metadata
        meta_df = pd.DataFrame([metadata])
        
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


# For backward compatibility and convenience
def il_cbs_api_simple(series_id: Union[str, int], **kwargs) -> pd.DataFrame:
    """
    Simplified version that returns only the data DataFrame.
    
    Parameters same as il_cbs_api, returns only the time series data.
    """
    data_df, _ = il_cbs_api(series_id, **kwargs)
    return data_df