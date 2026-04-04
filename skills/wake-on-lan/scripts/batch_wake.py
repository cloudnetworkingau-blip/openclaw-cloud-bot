#!/usr/bin/env python3
"""
Batch Wake-on-LAN processor with enhanced features.

This script provides advanced batch processing capabilities including:
- JSON/YAML configuration support
- Scheduled waking
- Retry logic
- Status reporting
"""

import argparse
import csv
import json
import time
import yaml
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from wake_pc import send_wol_packet, wake_by_ip


class BatchWaker:
    """Batch processor for Wake-on-LAN operations."""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.machines = []
        self.results = {}
        
    def load_config(self) -> bool:
        """Load configuration from file."""
        try:
            if self.config_path.suffix.lower() == '.json':
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
            elif self.config_path.suffix.lower() in ['.yaml', '.yml']:
                with open(self.config_path, 'r') as f:
                    config = yaml.safe_load(f)
            elif self.config_path.suffix.lower() == '.csv':
                return self.load_csv_config()
            else:
                print(f"Unsupported file format: {self.config_path.suffix}")
                return False
            
            self.machines = config.get('machines', [])
            return True
            
        except Exception as e:
            print(f"Error loading config: {e}")
            return False
    
    def load_csv_config(self) -> bool:
        """Load configuration from CSV file."""
        try:
            with open(self.config_path, 'r') as f:
                reader = csv.DictReader(f)
                self.machines = list(reader)
            return True
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False
    
    def wake_machine(self, machine: Dict[str, Any], retries: int = 3) -> bool:
        """Wake a single machine with retry logic."""
        name = machine.get('name', 'unknown')
        mac = machine.get('mac')
        ip = machine.get('ip')
        broadcast = machine.get('broadcast', '255.255.255.255')
        port = int(machine.get('port', 9))
        
        print(f"\nWaking {name}...")
        print(f"  MAC: {mac if mac else 'Not specified'}")
        print(f"  IP: {ip if ip else 'Not specified'}")
        print(f"  Broadcast: {broadcast}")
        print(f"  Port: {port}")
        
        success = False
        for attempt in range(1, retries + 1):
            print(f"  Attempt {attempt}/{retries}...")
            
            if mac:
                success = send_wol_packet(mac, broadcast, port)
            elif ip:
                success = wake_by_ip(ip, broadcast, port)
            else:
                print(f"  ✗ No MAC or IP specified for {name}")
                break
            
            if success:
                break
            
            if attempt < retries:
                time.sleep(2)  # Wait before retry
        
        return success
    
    def wake_all(self, delay: float = 1.0) -> Dict[str, bool]:
        """Wake all machines in the configuration."""
        print(f"Starting batch wake of {len(self.machines)} machines")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        self.results = {}
        
        for i, machine in enumerate(self.machines, 1):
            print(f"\n[{i}/{len(self.machines)}] ", end="")
            success = self.wake_machine(machine)
            self.results[machine.get('name', f'machine_{i}')] = success
            
            if i < len(self.machines) and delay > 0:
                time.sleep(delay)
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate a summary report."""
        total = len(self.results)
        successful = sum(1 for success in self.results.values() if success)
        failed = total - successful
        
        report = [
            "\n" + "=" * 50,
            "BATCH WAKE REPORT",
            "=" * 50,
            f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total machines: {total}",
            f"Successful: {successful}",
            f"Failed: {failed}",
            ""
        ]
        
        if failed > 0:
            report.append("Failed machines:")
            for name, success in self.results.items():
                if not success:
                    report.append(f"  - {name}")
        
        return "\n".join(report)


def create_example_config(output_path: Path, format: str = 'json') -> None:
    """Create an example configuration file."""
    example_config = {
        'machines': [
            {
                'name': 'office-pc',
                'mac': 'AA:BB:CC:DD:EE:FF',
                'ip': '192.168.0.200',
                'broadcast': '192.168.0.255',
                'port': 9,
                'description': 'Main office computer'
            },
            {
                'name': 'nas-server',
                'mac': '11:22:33:44:55:66',
                'ip': '192.168.0.201',
                'broadcast': '192.168.0.255',
                'port': 7,
                'description': 'Network attached storage'
            },
            {
                'name': 'media-center',
                'mac': 'AA:11:BB:22:CC:33',
                'ip': '192.168.0.202',
                'broadcast': '192.255.255.255',
                'port': 9,
                'description': 'Home theater PC'
            }
        ]
    }
    
    try:
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(example_config, f, indent=2)
        elif format in ['yaml', 'yml']:
            with open(output_path, 'w') as f:
                yaml.dump(example_config, f, default_flow_style=False)
        elif format == 'csv':
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'mac', 'ip', 'broadcast', 'port', 'description'])
                writer.writeheader()
                for machine in example_config['machines']:
                    writer.writerow(machine)
        
        print(f"Created example configuration: {output_path}")
        
    except Exception as e:
        print(f"Error creating example config: {e}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Batch Wake-on-LAN processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process JSON configuration
  %(prog)s --config machines.json
  
  # Process YAML configuration
  %(prog)s --config machines.yaml
  
  # Process CSV configuration
  %(prog)s --config machines.csv
  
  # Create example configuration
  %(prog)s --create-example example.json
  %(prog)s --create-example example.yaml --format yaml
  %(prog)s --create-example example.csv --format csv
  
  # With delay between machines
  %(prog)s --config machines.json --delay 2.5
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        type=Path,
        help="Configuration file (JSON, YAML, or CSV)"
    )
    
    parser.add_argument(
        '--create-example',
        type=Path,
        help="Create an example configuration file"
    )
    
    parser.add_argument(
        '--format',
        choices=['json', 'yaml', 'yml', 'csv'],
        default='json',
        help="Format for example creation (default: json)"
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help="Delay between machines in seconds (default: 1.0)"
    )
    
    parser.add_argument(
        '--retries',
        type=int,
        default=3,
        help="Number of retry attempts per machine (default: 3)"
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Handle example creation
    if args.create_example:
        create_example_config(args.create_example, args.format)
        return
    
    # Handle batch processing
    if args.config:
        if not args.config.exists():
            print(f"Error: Configuration file not found: {args.config}")
            return
        
        waker = BatchWaker(args.config)
        
        if not waker.load_config():
            print("Failed to load configuration")
            return
        
        if args.verbose:
            print(f"Loaded {len(waker.machines)} machines from {args.config}")
        
        waker.wake_all(args.delay)
        print(waker.generate_report())
        
        # Exit with error code if any failures
        successful = sum(1 for success in waker.results.values() if success)
        if successful < len(waker.results):
            sys.exit(1)
    
    else:
        print("Error: No configuration specified")
        parser.print_help()


if __name__ == '__main__':
    import sys
    main()