import type {
  ReportCategoryItem,
} from "../api/types";
import {
  formatCurrency,
} from "../utils/formatters";


interface BreakdownBarsProps {
  items: ReportCategoryItem[];
}


export function BreakdownBars({
  items,
}: BreakdownBarsProps) {
  if (items.length === 0) {
    return (
      <p className="empty-copy">
        Nenhuma categoria encontrada no periodo.
      </p>
    );
  }

  return (
    <div className="breakdown-list">
      {items.map((item) => (
        <div
          className="breakdown-item"
          key={item.name}
        >
          <div className="breakdown-heading">
            <strong>{item.name}</strong>
            <span>
              {formatCurrency(
                item.total
              )}
              {" - "}
              {item.percentage}%
            </span>
          </div>

          <div
            aria-label={`${item.name}: ${item.percentage}%`}
            className="breakdown-track"
            role="progressbar"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={
              Number(
                item.percentage
              )
            }
          >
            <span
              style={{
                width: `${
                  Math.min(
                    Number(
                      item.percentage
                    ),
                    100,
                  )
                }%`,
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
