import psutil
import platform
from datetime import datetime
import subprocess


def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def run_sys_diag(logger):
    logger.info("="*40 + "System Information" + "="*40)
    uname = platform.uname()
    logger.info(f"System: {uname.system}")
    logger.info(f"Node Name: {uname.node}")
    logger.info(f"Release: {uname.release}")
    logger.info(f"Version: {uname.version}")
    logger.info(f"Machine: {uname.machine}")
    logger.info(f"Processor: {uname.processor}")

    # Boot Time
    logger.info("="*40 + "Boot Time" + "="*40)
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    logger.info(f"Boot Time: {bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}")

    # let's logger.info CPU information
    logger.info("="*40 + "CPU Info" + "="*40)
    # number of cores
    logger.info("Physical cores:" + str(psutil.cpu_count(logical=False)))
    logger.info("Total cores:" + str(psutil.cpu_count(logical=True)))
    # CPU frequencies
    try:
        cpufreq = psutil.cpu_freq()
        max_cpufreq = f"{cpufreq.max:.2f}"
        min_cpufreq = f"{cpufreq.min:.2f}"
        cur_cpufreq = f"{cpufreq.current:.2f}"
    except Exception as e:
        try:
            cur_cpufreq = float(subprocess.check_output(["sysctl", "-n", "hw.cpufrequency"]).strip()) / 10**9  # Convert Hz to GHz
            max_cpufreq = float(subprocess.check_output(["sysctl", "-n", "hw.cpufrequency_max"]).strip()) / 10**9  # Convert Hz to GHz
            min_cpufreq = float(subprocess.check_output(["sysctl", "-n", "hw.cpufrequency_min"]).strip()) / 10**9  # Convert Hz to GHz
        except Exception as e:
            logger.info(f"Could not determine CPU frequency due to {str(e)}. Continuing...")

    logger.info(f"Max Frequency: {max_cpufreq}Mhz")
    logger.info(f"Min Frequency: {min_cpufreq}Mhz")
    logger.info(f"Current Frequency: {cur_cpufreq}Mhz")
    # CPU usage
    logger.info("CPU Usage Per Core:")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        logger.info(f"Core {i}: {percentage}%")
    logger.info(f"Total CPU Usage: {psutil.cpu_percent()}%")


    # Memory Information
    logger.info("="*40 + "Memory Information" + "="*40)
    # get the memory details
    svmem = psutil.virtual_memory()
    logger.info(f"Total: {get_size(svmem.total)}")
    logger.info(f"Available: {get_size(svmem.available)}")
    logger.info(f"Used: {get_size(svmem.used)}")
    logger.info(f"Percentage: {svmem.percent}%")
    logger.info("="*20 + "SWAP" + "="*20)
    # get the swap memory details (if exists)
    swap = psutil.swap_memory()
    logger.info(f"Total: {get_size(swap.total)}")
    logger.info(f"Free: {get_size(swap.free)}")
    logger.info(f"Used: {get_size(swap.used)}")
    logger.info(f"Percentage: {swap.percent}%")


    # Disk Information
    logger.info("="*40 + "Disk Information" + "="*40)
    logger.info("Partitions and Usage:")
    # get all disk partitions
    partitions = psutil.disk_partitions()
    for partition in partitions:
        logger.info(f"=== Device: {partition.device} ===")
        logger.info(f"  Mountpoint: {partition.mountpoint}")
        logger.info(f"  File system type: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # this can be catched due to the disk that
            # isn't ready
            continue
        logger.info(f"  Total Size: {get_size(partition_usage.total)}")
        logger.info(f"  Used: {get_size(partition_usage.used)}")
        logger.info(f"  Free: {get_size(partition_usage.free)}")
        logger.info(f"  Percentage: {partition_usage.percent}%")
    # get IO statistics since boot
    disk_io = psutil.disk_io_counters()
    logger.info(f"Total read: {get_size(disk_io.read_bytes)}")
    logger.info(f"Total write: {get_size(disk_io.write_bytes)}")

    # Network information
    logger.info("="*40 + "Network Information" + "="*40)
    # get all network interfaces (virtual and physical)
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            logger.info(f"=== Interface: {interface_name} ===")
            if str(address.family) == 'AddressFamily.AF_INET':
                logger.info(f"  IP Address: {address.address}")
                logger.info(f"  Netmask: {address.netmask}")
                logger.info(f"  Broadcast IP: {address.broadcast}")
            elif str(address.family) == 'AddressFamily.AF_PACKET':
                logger.info(f"  MAC Address: {address.address}")
                logger.info(f"  Netmask: {address.netmask}")
                logger.info(f"  Broadcast MAC: {address.broadcast}")
    # get IO statistics since boot
    net_io = psutil.net_io_counters()
    logger.info(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
    logger.info(f"Total Bytes Received: {get_size(net_io.bytes_recv)}")