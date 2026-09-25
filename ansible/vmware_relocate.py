#!/usr/bin/env python3

import argparse
import getpass
import ssl
import sys

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim


def find_vm_by_moid(content, moid):
    search_index = content.searchIndex

    vm = search_index.FindByInventoryPath(
        f"/LBH/vm/HSST/{moid}"
    )

    if vm is not None:
        return vm

    # Search inventory if the path lookup above does not work.
    view = content.viewManager.CreateContainerView(
        content.rootFolder,
        [vim.VirtualMachine],
        True,
    )

    try:
        for obj in view.view:
            if obj._moId == moid:
                return obj
    finally:
        view.Destroy()

    return None


def find_datastore(content, name):
    view = content.viewManager.CreateContainerView(
        content.rootFolder,
        [vim.Datastore],
        True,
    )

    try:
        for ds in view.view:
            if ds.name == name:
                return ds
    finally:
        view.Destroy()

    return None


def find_host(content, name):
    view = content.viewManager.CreateContainerView(
        content.rootFolder,
        [vim.HostSystem],
        True,
    )

    try:
        for host in view.view:
            if host.name == name:
                return host
    finally:
        view.Destroy()

    return None


def find_resource_pool(content, name):
    view = content.viewManager.CreateContainerView(
        content.rootFolder,
        [vim.ResourcePool],
        True,
    )

    try:
        for pool in view.view:
            if pool.name == name:
                return pool
    finally:
        view.Destroy()

    return None


def find_network(content, name):
    view = content.viewManager.CreateContainerView(
        content.rootFolder,
        [
            vim.dvs.DistributedVirtualPortgroup,
            vim.Network,
        ],
        True,
    )

    try:
        for network in view.view:
            if network.name == name:
                return network
    finally:
        view.Destroy()

    return None


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--host", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)

    parser.add_argument("--moid", required=True)

    parser.add_argument("--destination-host", required=True)
    parser.add_argument("--destination-pool", required=True)
    parser.add_argument("--destination-datastore", required=True)
    parser.add_argument("--destination-network", required=True)

    args = parser.parse_args()

    context = ssl._create_unverified_context()

    si = SmartConnect(
        host=args.host,
        user=args.username,
        pwd=args.password,
        sslContext=context,
    )

    try:
        content = si.RetrieveContent()

        # ---------------------------------------------------------
        # Find VM by MoID
        # ---------------------------------------------------------

        vm = None

        view = content.viewManager.CreateContainerView(
            content.rootFolder,
            [vim.VirtualMachine],
            True,
        )

        try:
            for obj in view.view:
                if obj._moId == args.moid:
                    vm = obj
                    break
        finally:
            view.Destroy()

        if vm is None:
            raise RuntimeError(
                f"VM with MoID {args.moid} was not found"
            )

        print(f"VM: {vm.name}")
        print(f"MoID: {vm._moId}")
        print(f"Power state: {vm.runtime.powerState}")

        # ---------------------------------------------------------
        # Destination host
        # ---------------------------------------------------------

        destination_host = find_host(
            content,
            args.destination_host,
        )

        if destination_host is None:
            raise RuntimeError(
                f"Destination host not found: "
                f"{args.destination_host}"
            )

        print(
            f"Destination host: "
            f"{destination_host.name}"
        )

        # ---------------------------------------------------------
        # Destination resource pool
        # ---------------------------------------------------------

        destination_pool = find_resource_pool(
            content,
            args.destination_pool,
        )

        if destination_pool is None:
            raise RuntimeError(
                f"Destination resource pool not found: "
                f"{args.destination_pool}"
            )

        print(
            f"Destination pool: "
            f"{destination_pool.name}"
        )

        # ---------------------------------------------------------
        # Destination datastore
        # ---------------------------------------------------------

        destination_datastore = find_datastore(
            content,
            args.destination_datastore,
        )

        if destination_datastore is None:
            raise RuntimeError(
                f"Destination datastore not found: "
                f"{args.destination_datastore}"
            )

        print(
            f"Destination datastore: "
            f"{destination_datastore.name}"
        )

        # ---------------------------------------------------------
        # Destination network
        # ---------------------------------------------------------

        destination_network = find_network(
            content,
            args.destination_network,
        )

        if destination_network is None:
            raise RuntimeError(
                f"Destination network not found: "
                f"{args.destination_network}"
            )

        print(
            f"Destination network: "
            f"{destination_network.name}"
        )

        # ---------------------------------------------------------
        # Verify NIC
        # ---------------------------------------------------------

        nics = [
            device
            for device in vm.config.hardware.device
            if isinstance(device, vim.vm.device.VirtualEthernetCard)
        ]

        if len(nics) != 1:
            raise RuntimeError(
                f"Expected exactly one NIC, found {len(nics)}"
            )

        nic = nics[0]

        print(f"NIC: {nic.deviceInfo.label}")

        # ---------------------------------------------------------
        # Build destination backing
        # ---------------------------------------------------------

        if not isinstance(
            destination_network,
            vim.dvs.DistributedVirtualPortgroup,
        ):
            raise RuntimeError(
                "Destination network is not a "
                "DistributedVirtualPortgroup"
            )

        dvs = destination_network.config.distributedVirtualSwitch

        portgroup_key = destination_network.key

        print(f"Destination DVS: {dvs.name}")
        print(f"Destination DVPG key: {portgroup_key}")

        # ---------------------------------------------------------
        # Build DistributedVirtualPort backing
        # ---------------------------------------------------------

        port_connection = vim.dvs.PortConnection()
        port_connection.portgroupKey = portgroup_key
        port_connection.switchUuid = dvs.uuid

        distributed_backing = (
            vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
        )

        distributed_backing.port = port_connection

        # ---------------------------------------------------------
        # NIC edit
        # ---------------------------------------------------------

        nic_spec = vim.vm.device.VirtualDeviceSpec()
        nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
        nic_spec.device = nic
        nic_spec.device.backing = distributed_backing

        # Preserve connection state.
        if nic.connectable is not None:
            nic_spec.device.connectable = nic.connectable

        # ---------------------------------------------------------
        # Relocate spec
        # ---------------------------------------------------------

        relocate_spec = vim.vm.RelocateSpec()

        relocate_spec.host = destination_host
        relocate_spec.pool = destination_pool
        relocate_spec.datastore = destination_datastore

        relocate_spec.deviceChange = [
            nic_spec
        ]

        # ---------------------------------------------------------
        # Start relocation
        # ---------------------------------------------------------

        print()
        print("Starting RelocateVM_Task...")
        print("------------------------------------------")

        task = vm.RelocateVM_Task(
            spec=relocate_spec,
            priority=vim.VirtualMachine.MovePriority.defaultPriority,
        )

        # ---------------------------------------------------------
        # Wait for task
        # ---------------------------------------------------------

        while task.info.state in (
            vim.TaskInfo.State.queued,
            vim.TaskInfo.State.running,
        ):
            pass

        if task.info.state != vim.TaskInfo.State.success:
            error = task.info.error
            raise RuntimeError(
                f"RelocateVM_Task failed: {error}"
            )

        print("------------------------------------------")
        print("Migration completed successfully")
        print(f"VM: {vm.name}")
        print(f"MoID: {vm._moId}")
        print(
            f"Destination host: "
            f"{destination_host.name}"
        )
        print(
            f"Destination datastore: "
            f"{destination_datastore.name}"
        )
        print(
            f"Destination network: "
            f"{destination_network.name}"
        )

    finally:
        Disconnect(si)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
