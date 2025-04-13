"""
Command line interface for the video processing pipeline
"""
import os
import sys
import argparse
import logging

from video_pipeline.core.pipeline import Pipeline
from video_pipeline.utils.logger import setup_logger
from video_pipeline.utils.ffmpeg import check_ffmpeg_installed
from video_pipeline.config.generate_examples import generate_example_config

def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Object with arguments
    """
    parser = argparse.ArgumentParser(
        description="Video processing pipeline using YAML configuration"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Парсер для обработки видео
    process_parser = subparsers.add_parser("process", help="Process video using configuration")
    process_parser.add_argument(
        "-c", "--config", 
        required=True,
        help="Path to YAML configuration file"
    )
    process_parser.add_argument(
        "-i", "--input",
        help="Path to input video (overrides value from configuration)"
    )
    process_parser.add_argument(
        "-o", "--output",
        help="Path to output video (overrides value from configuration)"
    )
    process_parser.add_argument(
        "-l", "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    process_parser.add_argument(
        "--log-file",
        help="Path to log file (if not specified, logs are output to console only)"
    )
    process_parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip dependency checks (FFmpeg)"
    )
    
    # Парсер для генерации примеров
    generate_parser = subparsers.add_parser("generate", help="Generate example configuration")
    generate_parser.add_argument(
        "-o", "--output",
        help="Path to output YAML file (default: example_config.yaml in config directory)"
    )
    generate_parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Overwrite existing file"
    )
    
    return parser.parse_args()

def main():
    """
    Main function to run the pipeline.
    """
    # Parse command line arguments
    args = parse_args()
    
    if args.command == "process":
        # Set up logging
        logger = setup_logger(args.log_level, args.log_file)
        
        # Check dependencies
        if not args.skip_checks:
            logger.info("Checking FFmpeg...")
            if not check_ffmpeg_installed():
                logger.error("FFmpeg is not installed or not found in PATH.")
                logger.error("Install FFmpeg or run with --skip-checks flag to skip this check.")
                sys.exit(1)
        
        # Check if configuration file exists
        if not os.path.exists(args.config):
            logger.error(f"Configuration file not found: {args.config}")
            sys.exit(1)
        
        try:
            # Create and run the pipeline
            pipeline = Pipeline(args.config)
            pipeline.process(args.input, args.output)
            logger.info("Video processing completed successfully")
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}", exc_info=True)
            sys.exit(1)
            
    elif args.command == "generate":
        # Генерируем пример конфигурации
        example_config = generate_example_config()
        
        # Определяем путь для сохранения
        if args.output:
            output_path = args.output
        else:
            output_path = os.path.join(os.path.dirname(__file__), "config", "example_config.yaml")
            
        # Проверяем существование файла
        if os.path.exists(output_path) and not args.force:
            print(f"File {output_path} already exists. Use -f to overwrite.")
            sys.exit(1)
            
        # Сохраняем конфигурацию
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                import yaml
                yaml.dump(example_config, f, allow_unicode=True, sort_keys=False)
            print(f"Example configuration saved to {output_path}")
        except Exception as e:
            print(f"Error saving example configuration: {str(e)}")
            sys.exit(1)
            
    else:
        print("Please specify a command: process or generate")
        sys.exit(1)

if __name__ == "__main__":
    main() 