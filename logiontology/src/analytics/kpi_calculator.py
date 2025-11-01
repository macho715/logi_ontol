"""
HVDC Flow KPI Calculator v1.0
Calculates logistics KPIs from flow instances
"""

from typing import List
from dataclasses import dataclass, asdict
from collections import Counter
from ..core.flow_models import LogisticsFlow, FlowCode


@dataclass
class FlowKPIs:
    """Flow KPI metrics"""
    total_flows: int
    pre_arrival_count: int
    direct_delivery_rate: float  # Percentage of FlowCode=1
    mosb_pass_rate: float  # Percentage with offshore_flag=True
    avg_wh_hops: float
    flow_distribution: dict[int, int]  # FlowCode → count
    mode_distribution: dict[str, int]  # transport_mode → count

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)

    def summary(self) -> str:
        """Generate summary report"""
        lines = [
            "=== HVDC Flow KPI Summary ===",
            f"Total Flows: {self.total_flows}",
            f"Pre-Arrival: {self.pre_arrival_count} ({self.pre_arrival_count/max(self.total_flows,1)*100:.1f}%)",
            f"Direct Delivery Rate: {self.direct_delivery_rate:.2f}%",
            f"MOSB Pass Rate: {self.mosb_pass_rate:.2f}%",
            f"Average WH Hops: {self.avg_wh_hops:.2f}",
            "",
            "Flow Code Distribution:",
        ]
        for code in sorted(self.flow_distribution.keys()):
            count = self.flow_distribution[code]
            pct = count / max(self.total_flows, 1) * 100
            lines.append(f"  Code {code}: {count} ({pct:.1f}%)")

        lines.append("")
        lines.append("Transport Mode Distribution:")
        for mode, count in sorted(self.mode_distribution.items()):
            pct = count / max(self.total_flows, 1) * 100
            lines.append(f"  {mode}: {count} ({pct:.1f}%)")

        return "\n".join(lines)


class FlowKPICalculator:
    """Calculate KPIs from logistics flow instances"""

    def calculate(self, flows: List[LogisticsFlow]) -> FlowKPIs:
        """
        Calculate comprehensive KPIs from flow instances

        Args:
            flows: List of LogisticsFlow instances

        Returns:
            FlowKPIs with all metrics calculated
        """
        total = len(flows)

        if total == 0:
            return FlowKPIs(
                total_flows=0,
                pre_arrival_count=0,
                direct_delivery_rate=0.0,
                mosb_pass_rate=0.0,
                avg_wh_hops=0.0,
                flow_distribution={},
                mode_distribution={}
            )

        # Count metrics
        pre_arrival = sum(1 for f in flows if f.is_pre_arrival)
        direct = sum(1 for f in flows if f.flow_code == FlowCode.DIRECT)
        mosb_pass = sum(1 for f in flows if f.offshore_flag)
        total_wh = sum(f.wh_handling for f in flows)

        # Flow code distribution
        flow_dist = Counter(int(f.flow_code) for f in flows)

        # Transport mode distribution
        mode_dist = Counter(f.transport_mode for f in flows)

        return FlowKPIs(
            total_flows=total,
            pre_arrival_count=pre_arrival,
            direct_delivery_rate=(direct / total * 100) if total > 0 else 0.0,
            mosb_pass_rate=(mosb_pass / total * 100) if total > 0 else 0.0,
            avg_wh_hops=(total_wh / total) if total > 0 else 0.0,
            flow_distribution=dict(flow_dist),
            mode_distribution=dict(mode_dist)
        )

    def calculate_by_mode(self, flows: List[LogisticsFlow]) -> dict[str, FlowKPIs]:
        """
        Calculate KPIs grouped by transport mode

        Args:
            flows: List of LogisticsFlow instances

        Returns:
            Dictionary mapping transport_mode → FlowKPIs
        """
        from itertools import groupby

        # Group by transport mode
        sorted_flows = sorted(flows, key=lambda f: f.transport_mode)
        grouped = {
            mode: list(group)
            for mode, group in groupby(sorted_flows, key=lambda f: f.transport_mode)
        }

        # Calculate KPIs for each mode
        return {
            mode: self.calculate(mode_flows)
            for mode, mode_flows in grouped.items()
        }

    def validate_consistency(self, flows: List[LogisticsFlow]) -> tuple[int, List[str]]:
        """
        Validate flow code consistency across all flows

        Args:
            flows: List of LogisticsFlow instances

        Returns:
            Tuple of (valid_count, list of error messages)
        """
        errors = []
        valid = 0

        for flow in flows:
            if flow.validate_consistency():
                valid += 1
            else:
                expected = LogisticsFlow.calculate_flow_code(
                    flow.wh_handling,
                    flow.offshore_flag,
                    flow.is_pre_arrival
                )
                errors.append(
                    f"Flow {flow.flow_id}: FlowCode={flow.flow_code} but expected {expected} "
                    f"(WH={flow.wh_handling}, Offshore={flow.offshore_flag}, PreArrival={flow.is_pre_arrival})"
                )

        return valid, errors

