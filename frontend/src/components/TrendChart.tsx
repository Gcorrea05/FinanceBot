import type {
  ReportMonthlyPoint,
} from "../api/types";
import {
  formatCurrency,
} from "../utils/formatters";


interface TrendChartProps {
  items: ReportMonthlyPoint[];
}


export function TrendChart({
  items,
}: TrendChartProps) {
  const width = 720;
  const height = 250;
  const paddingX = 42;
  const paddingY = 34;

  const values = items.map(
    (item) => Number(item.total)
  );

  const maximum = Math.max(
    ...values,
    1,
  );

  const innerWidth = (
    width
    - paddingX * 2
  );

  const innerHeight = (
    height
    - paddingY * 2
  );

  const points = items.map(
    (item, index) => {
      const x = (
        items.length <= 1
          ? width / 2
          : paddingX
            + (
                index
                / (items.length - 1)
              )
              * innerWidth
      );

      const y = (
        height
        - paddingY
        - (
            Number(item.total)
            / maximum
          )
          * innerHeight
      );

      return {
        ...item,
        x,
        y,
      };
    }
  );

  const polyline = points
    .map(
      (point) =>
        `${point.x},${point.y}`
    )
    .join(" ");

  if (items.length === 0) {
    return (
      <p className="empty-copy">
        Nenhum valor para exibir.
      </p>
    );
  }

  return (
    <div className="trend-chart">
      <svg
        aria-label="Evolucao mensal dos gastos"
        role="img"
        viewBox={`0 0 ${width} ${height}`}
      >
        <line
          className="chart-axis"
          x1={paddingX}
          x2={width - paddingX}
          y1={height - paddingY}
          y2={height - paddingY}
        />

        <polyline
          className="chart-line"
          fill="none"
          points={polyline}
        />

        {points.map((point) => (
          <g key={`${point.year}-${point.month}`}>
            <circle
              className="chart-point"
              cx={point.x}
              cy={point.y}
              r="5"
            />

            <text
              className="chart-value"
              textAnchor="middle"
              x={point.x}
              y={Math.max(
                point.y - 12,
                18,
              )}
            >
              {formatCurrency(
                point.total
              )}
            </text>

            <text
              className="chart-label"
              textAnchor="middle"
              x={point.x}
              y={height - 10}
            >
              {point.label}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}
