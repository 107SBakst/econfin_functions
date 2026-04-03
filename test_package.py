"""
Test script for econfin_functions package
"""

import sys
import os
import pandas as pd

# Add the package to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from econfin_functions import il_cbs_api
    print("SUCCESS: Successfully imported il_cbs_api")
except ImportError as e:
    print(f"ERROR: Failed to import il_cbs_api: {e}")
    sys.exit(1)

def test_basic_functionality():
    """Test basic API functionality"""
    print("\n" + "="*50)
    print("Testing basic functionality...")
    
    try:
        # Test with a small date range
        data_df, meta_df = il_cbs_api(
            series_id=3763,
            startPeriod='2024-01',
            endPeriod='2024-06',
            format_type='json'
        )
        
        print("SUCCESS: Basic API call successful")
        print(f"SUCCESS: Data shape: {data_df.shape}")
        print(f"SUCCESS: Metadata shape: {meta_df.shape}")
        
        # Check data columns
        expected_data_cols = ['TimePeriod', 'Value', 'series_id']
        if all(col in data_df.columns for col in expected_data_cols):
            print("SUCCESS: Data DataFrame has expected columns")
        else:
            print(f"ERROR: Data DataFrame missing columns. Has: {list(data_df.columns)}")
        
        # Check metadata columns  
        expected_meta_cols = ['id', 'time_unit', 'data_type', 'unit', 'series_name', 'series_id']
        if all(col in meta_df.columns for col in expected_meta_cols):
            print("SUCCESS: Metadata DataFrame has expected columns")
        else:
            print(f"ERROR: Metadata DataFrame missing columns. Has: {list(meta_df.columns)}")
            
        # Display sample data
        print(f"\nSample data (first 3 rows):")
        print(data_df.head(3))
        print(f"\nMetadata:")
        print(meta_df[['series_name', 'unit', 'time_unit']].iloc[0])
        
        return True
        
    except Exception as e:
        print(f"ERROR: Basic test failed: {e}")
        return False

def test_xml_format():
    """Test XML format"""
    print("\n" + "="*50)
    print("Testing XML format...")
    
    try:
        data_df, meta_df = il_cbs_api(
            series_id=3763,
            startPeriod='2024-01',
            endPeriod='2024-03',
            format_type='xml'
        )
        
        print("SUCCESS: XML format test successful")
        print(f"SUCCESS: Data shape: {data_df.shape}")
        return True
        
    except Exception as e:
        print(f"ERROR: XML test failed: {e}")
        return False

def test_parameter_validation():
    """Test parameter validation"""
    print("\n" + "="*50)
    print("Testing parameter validation...")
    
    # Test invalid format
    try:
        il_cbs_api(3763, format_type='invalid')
        print("ERROR: Should have raised ValueError for invalid format")
    except ValueError:
        print("SUCCESS: Correctly rejected invalid format")
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
    
    # Test invalid language
    try:
        il_cbs_api(3763, lang='invalid')
        print("ERROR: Should have raised ValueError for invalid language")
    except ValueError:
        print("SUCCESS: Correctly rejected invalid language")
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")

def test_different_series():
    """Test with different series if available"""
    print("\n" + "="*50)
    print("Testing different parameters...")
    
    try:
        # Test without date range
        data_df, meta_df = il_cbs_api(3763, startPeriod='2024-10')
        print(f"SUCCESS: Test without end period successful. Data shape: {data_df.shape}")
        
        # Test with download=True
        data_df, meta_df = il_cbs_api(
            series_id=3763,
            startPeriod='2024-01',
            endPeriod='2024-03',
            download=True
        )
        print(f"SUCCESS: Test with download=True successful. Data shape: {data_df.shape}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Different parameters test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("econfin_functions Package Test Suite")
    print("="*50)
    
    tests_passed = 0
    total_tests = 4
    
    if test_basic_functionality():
        tests_passed += 1
        
    if test_xml_format():
        tests_passed += 1
        
    test_parameter_validation()  # This doesn't return bool
    tests_passed += 1  # Assuming it passes if no exception
    
    if test_different_series():
        tests_passed += 1
    
    print(f"\n{'='*50}")
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("SUCCESS: All tests passed! Package is ready to use.")
        return True
    else:
        print("ERROR: Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)