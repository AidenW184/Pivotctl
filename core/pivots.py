"""Pivot topology management for Pivotctl."""

import ipaddress


VALID_PIVOT_TOOLS = (
    "ssh",
    "chisel",
    "ligolo-ng",
    "socat",
    "sshuttle",
    "other",
)


class PivotManager:
    """Manage the current Pivotctl pivot topology."""

    def __init__(self):
        self.pivots = []


    def validate_ip(self, address):
        """Validate an IPv4 or IPv6 address."""

        try:
            ipaddress.ip_address(address)
            return True

        except ValueError:
            return False


    def validate_network(self, network):
        """Validate an IPv4 or IPv6 network."""

        try:
            ipaddress.ip_network(
                network,
                strict=False
            )
            return True

        except ValueError:
            return False


    def validate_port(self, port):
        """Validate a TCP/UDP port number."""

        if port in (
            None,
            "",
        ):
            return True

        try:
            port = int(port)

        except (
            TypeError,
            ValueError
        ):
            return False

        return 1 <= port <= 65535


    def validate_tool(self, tool):
        """Validate a supported pivot tool."""

        if not isinstance(tool, str):
            return False

        return (
            tool.strip().lower()
            in VALID_PIVOT_TOOLS
        )


    def normalise_network(self, network):
        """Return a network in canonical CIDR form."""

        return str(
            ipaddress.ip_network(
                network,
                strict=False
            )
        )


    def get_pivots(self):
        """Return all configured pivots."""

        return self.pivots.copy()


    def get_pivot(self, pivot_id):
        """Return a pivot by its internal ID."""

        for pivot in self.pivots:

            if pivot["id"] == pivot_id:
                return pivot

        raise ValueError(
            f"Pivot ID does not exist: {pivot_id}"
        )


    def get_next_id(self):
        """Return the next available pivot ID."""

        if not self.pivots:
            return 1

        return max(
            pivot["id"]
            for pivot in self.pivots
        ) + 1


    def add_pivot(
        self,
        name,
        address,
        networks,
        tool="ssh",
        parent_id=None,
        local_port=None,
        notes=""
    ):
        """Add a pivot to the current topology."""

        name = name.strip()
        address = address.strip()
        tool = tool.strip().lower()
        notes = notes.strip()

        if not name:
            raise ValueError(
                "Pivot name cannot be empty."
            )

        if not self.validate_ip(address):
            raise ValueError(
                f"Invalid pivot IP address: {address}"
            )

        if not self.validate_tool(tool):
            raise ValueError(
                f"Unsupported pivot tool: {tool}"
            )

        if not self.validate_port(local_port):
            raise ValueError(
                f"Invalid local port: {local_port}"
            )

        if isinstance(networks, str):
            networks = [networks]

        if not networks:
            raise ValueError(
                "At least one reachable network "
                "must be provided."
            )

        normalised_networks = []

        for network in networks:

            network = network.strip()

            if not self.validate_network(network):
                raise ValueError(
                    f"Invalid network: {network}"
                )

            normalised = self.normalise_network(
                network
            )

            if normalised not in normalised_networks:
                normalised_networks.append(
                    normalised
                )

        if parent_id is not None:

            try:
                parent_id = int(parent_id)

            except (
                TypeError,
                ValueError
            ) as error:
                raise ValueError(
                    "Parent pivot ID must be a number."
                ) from error

            self.get_pivot(parent_id)

        if local_port not in (
            None,
            "",
        ):
            local_port = int(local_port)

        else:
            local_port = None

        for existing in self.pivots:

            if existing["name"].lower() == name.lower():
                raise ValueError(
                    f"Pivot name already exists: {name}"
                )

            if existing["address"] == address:
                raise ValueError(
                    f"Pivot address already exists: "
                    f"{address}"
                )

        pivot = {
            "id": self.get_next_id(),
            "name": name,
            "address": address,
            "networks": normalised_networks,
            "tool": tool,
            "parent_id": parent_id,
            "local_port": local_port,
            "notes": notes,
        }

        self.pivots.append(pivot)

        return pivot.copy()


    def edit_pivot(
        self,
        pivot_id,
        name=None,
        address=None,
        networks=None,
        tool=None,
        parent_id=None,
        local_port=None,
        notes=None
    ):
        """Edit an existing pivot."""

        pivot = self.get_pivot(
            pivot_id
        )

        if name is not None:

            name = name.strip()

            if not name:
                raise ValueError(
                    "Pivot name cannot be empty."
                )

            for existing in self.pivots:

                if existing["id"] == pivot_id:
                    continue

                if (
                    existing["name"].lower()
                    == name.lower()
                ):
                    raise ValueError(
                        f"Pivot name already exists: "
                        f"{name}"
                    )

            pivot["name"] = name

        if address is not None:

            address = address.strip()

            if not self.validate_ip(address):
                raise ValueError(
                    f"Invalid pivot IP address: "
                    f"{address}"
                )

            for existing in self.pivots:

                if existing["id"] == pivot_id:
                    continue

                if existing["address"] == address:
                    raise ValueError(
                        f"Pivot address already exists: "
                        f"{address}"
                    )

            pivot["address"] = address

        if networks is not None:

            if isinstance(networks, str):
                networks = [networks]

            if not networks:
                raise ValueError(
                    "At least one reachable network "
                    "must be provided."
                )

            normalised_networks = []

            for network in networks:

                network = network.strip()

                if not self.validate_network(
                    network
                ):
                    raise ValueError(
                        f"Invalid network: {network}"
                    )

                normalised = self.normalise_network(
                    network
                )

                if (
                    normalised
                    not in normalised_networks
                ):
                    normalised_networks.append(
                        normalised
                    )

            pivot["networks"] = (
                normalised_networks
            )

        if tool is not None:

            tool = tool.strip().lower()

            if not self.validate_tool(tool):
                raise ValueError(
                    f"Unsupported pivot tool: "
                    f"{tool}"
                )

            pivot["tool"] = tool

        if parent_id is not None:

            if parent_id == "":
                pivot["parent_id"] = None

            else:
                try:
                    parent_id = int(parent_id)

                except (
                    TypeError,
                    ValueError
                ) as error:
                    raise ValueError(
                        "Parent pivot ID must "
                        "be a number."
                    ) from error

                if parent_id == pivot_id:
                    raise ValueError(
                        "A pivot cannot be its "
                        "own parent."
                    )

                self.get_pivot(parent_id)

                if self._creates_cycle(
                    pivot_id,
                    parent_id
                ):
                    raise ValueError(
                        "Parent relationship "
                        "would create a cycle."
                    )

                pivot["parent_id"] = parent_id

        if local_port is not None:

            if local_port == "":
                pivot["local_port"] = None

            else:
                if not self.validate_port(
                    local_port
                ):
                    raise ValueError(
                        f"Invalid local port: "
                        f"{local_port}"
                    )

                pivot["local_port"] = int(
                    local_port
                )

        if notes is not None:
            pivot["notes"] = notes.strip()

        return pivot.copy()


    def _creates_cycle(
        self,
        pivot_id,
        proposed_parent_id
    ):
        """Check whether a parent change creates a cycle."""

        current_id = proposed_parent_id
        visited = set()

        while current_id is not None:

            if current_id == pivot_id:
                return True

            if current_id in visited:
                return True

            visited.add(current_id)

            current = self.get_pivot(
                current_id
            )

            current_id = current[
                "parent_id"
            ]

        return False


    def remove_pivot(self, pivot_id):
        """Remove a pivot from the topology."""

        pivot = self.get_pivot(
            pivot_id
        )

        children = [
            item
            for item in self.pivots
            if item["parent_id"] == pivot_id
        ]

        if children:
            child_names = ", ".join(
                child["name"]
                for child in children
            )

            raise ValueError(
                "Cannot remove pivot while it "
                "has child pivots: "
                f"{child_names}"
            )

        self.pivots.remove(pivot)

        return pivot.copy()


    def add_network(
        self,
        pivot_id,
        network
    ):
        """Add a reachable network to a pivot."""

        pivot = self.get_pivot(
            pivot_id
        )

        network = network.strip()

        if not self.validate_network(network):
            raise ValueError(
                f"Invalid network: {network}"
            )

        network = self.normalise_network(
            network
        )

        if network in pivot["networks"]:
            raise ValueError(
                f"Network already exists: "
                f"{network}"
            )

        pivot["networks"].append(
            network
        )

        return network


    def remove_network(
        self,
        pivot_id,
        network
    ):
        """Remove a reachable network from a pivot."""

        pivot = self.get_pivot(
            pivot_id
        )

        network = self.normalise_network(
            network
        )

        if network not in pivot["networks"]:
            raise ValueError(
                f"Network does not exist: "
                f"{network}"
            )

        if len(pivot["networks"]) == 1:
            raise ValueError(
                "A pivot must have at least "
                "one reachable network."
            )

        pivot["networks"].remove(
            network
        )

        return network


    def get_children(self, pivot_id):
        """Return direct child pivots."""

        return [
            pivot
            for pivot in self.pivots
            if pivot["parent_id"] == pivot_id
        ]


    def get_root_pivots(self):
        """Return pivots with no parent."""

        return [
            pivot
            for pivot in self.pivots
            if pivot["parent_id"] is None
        ]


    def build_tree_lines(
        self,
        pivot,
        prefix=""
    ):
        """Build ASCII topology lines recursively."""

        port_text = ""

        if pivot["local_port"]:
            port_text = (
                f" | local:{pivot['local_port']}"
            )

        lines = [
            (
                f"{prefix}"
                f"└── {pivot['name']} "
                f"({pivot['address']}) "
                f"[{pivot['tool']}]"
                f"{port_text}"
            )
        ]

        network_prefix = (
            prefix + "    "
        )

        for network in pivot["networks"]:
            lines.append(
                f"{network_prefix}"
                f"├── Network: {network}"
            )

        children = self.get_children(
            pivot["id"]
        )

        for child in children:
            lines.extend(
                self.build_tree_lines(
                    child,
                    prefix + "    "
                )
            )

        return lines


    def display_pivots(self):
        """Display pivots in table form."""

        print()
        print("PIVOTS")
        print("-" * 90)

        if not self.pivots:
            print("No pivots configured.")
            print()
            return

        print(
            f"{'ID':<5}"
            f"{'NAME':<20}"
            f"{'ADDRESS':<20}"
            f"{'TOOL':<14}"
            f"{'PARENT':<10}"
            f"{'PORT'}"
        )

        print("-" * 90)

        for pivot in self.pivots:

            parent = (
                str(pivot["parent_id"])
                if pivot["parent_id"]
                is not None
                else "-"
            )

            port = (
                str(pivot["local_port"])
                if pivot["local_port"]
                is not None
                else "-"
            )

            print(
                f"{pivot['id']:<5}"
                f"{pivot['name']:<20}"
                f"{pivot['address']:<20}"
                f"{pivot['tool']:<14}"
                f"{parent:<10}"
                f"{port}"
            )

            for network in pivot[
                "networks"
            ]:
                print(
                    f"{'':<5}"
                    f"└─ {network}"
                )

        print()


    def display_topology(self):
        """Display the pivot topology as an ASCII tree."""

        print()
        print("PIVOT TOPOLOGY")
        print("-" * 70)
        print("ATTACKER")

        roots = self.get_root_pivots()

        if not roots:
            print(
                "└── No pivots configured."
            )
            print()
            return

        for pivot in roots:

            for line in self.build_tree_lines(
                pivot
            ):
                print(line)

        print()


pivot_manager = PivotManager()


if __name__ == "__main__":

    try:
        pivot_manager.display_pivots()
        pivot_manager.display_topology()

    except (
        ValueError,
        TypeError,
        IndexError
    ) as error:
        print(
            f"[!] {error}"
        )