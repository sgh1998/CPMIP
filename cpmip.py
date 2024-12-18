import os
import sys
import importlib
import logging
from datetime import datetime

class CPMIPController:
    def __init__(self):
        # Setup logging
        self.setup_logging()
        
        # List of scripts in desired execution order
        self.execution_order = [

            'asplanned',      # From IFC file
            'asbuilt',           # Detection


            #'FloorRec_single',   # Floor and Coulumns recognition
            'FloorRec_multi',  


            #'progress_single'     # Final quantification
            'progress_multi'     # Final quantification

        ]
        
        self.logger.info("CPMIP Controller initialized")

    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        # Setup logging with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f'logs/cpmip_run_{timestamp}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)

    def import_module(self, module_name):
        """Safely import a module"""
        try:
            return importlib.import_module(module_name)
        except ImportError as e:
            self.logger.error(f"Failed to import {module_name}: {str(e)}")
            return None

    def run_module(self, module_name):
        """Run a specific module"""
        self.logger.info(f"Starting execution of {module_name}")
        
        try:
            # Import the module
            module = self.import_module(module_name)
            if module is None:
                return False
            
            # Check if module has a main function
            if hasattr(module, 'main'):
                module.main()
            else:
                # Execute the module directly
                exec(f"import {module_name}")
            
            self.logger.info(f"Successfully completed {module_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing {module_name}: {str(e)}")
            return False

    def run_pipeline(self, start_from=None):
        """Run all scripts in order"""
        self.logger.info("Starting CPMIP pipeline execution")
        
        # Find starting point
        start_index = 0
        if start_from:
            try:
                start_index = self.execution_order.index(start_from)
                self.logger.info(f"Starting from {start_from}")
            except ValueError:
                self.logger.error(f"Invalid starting point: {start_from}")
                return False
        
        # Execute modules in order
        for module_name in self.execution_order[start_index:]:
            success = self.run_module(module_name)
            
            if not success:
                self.logger.error(f"Pipeline failed at {module_name}")
                return False
                
        self.logger.info("Pipeline completed successfully")
        return True

def main():
    # Create controller instance
    controller = CPMIPController()
    
    # You can start from a specific point if needed
    # controller.run_pipeline(start_from='asbuilt_analysis')
    
    # Or run the complete pipeline
    controller.run_pipeline()

if __name__ == "__main__":
    main()