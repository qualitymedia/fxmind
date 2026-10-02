"use client";

import React, { memo } from "react";

interface TradingViewWidgetProps {
  symbol?: string;
  theme?: "dark" | "light";
  interval?: string;
}

function TradingViewWidgetComponent({
  symbol = "FX:GBPUSD",
  theme = "dark",
  interval = "15",
}: TradingViewWidgetProps) {
  // Normalize symbol for TradingView iframe URL
  const tvSymbol = symbol.includes(":") ? symbol : `FX:${symbol}`;
  const tvInterval = interval === "H1" ? "60" : interval === "30m" ? "30" : "15";

  const iframeSrc = `https://s.tradingview.com/widgetembed/?frameElementId=tradingview_widget&symbol=${encodeURIComponent(
    tvSymbol
  )}&interval=${tvInterval}&hidesidetoolbar=0&symboledit=1&saveimage=1&toolbarbg=131722&studies=%5B%22STD%3AEMA%22%2C%22STD%3ARSI%22%5D&theme=${theme}&style=1&timezone=Etc%2FUTC&studies_overrides=%7B%7D&overrides=%7B%22mainSeriesProperties.candleStyle.upColor%22%3A%22%2310B981%22%2C%22mainSeriesProperties.candleStyle.downColor%22%3A%22%23EF4444%22%2C%22mainSeriesProperties.candleStyle.borderUpColor%22%3A%22%2310B981%22%2C%22mainSeriesProperties.candleStyle.borderDownColor%22%3A%22%23EF4444%22%2C%22mainSeriesProperties.candleStyle.wickUpColor%22%3A%22%2310B981%22%2C%22mainSeriesProperties.candleStyle.wickDownColor%22%3A%22%23EF4444%22%7D&enabled_features=%5B%5D&disabled_features=%5B%5D&locale=en&utm_source=localhost&utm_medium=widget&utm_campaign=chart&utm_term=${encodeURIComponent(
    tvSymbol
  )}`;

  return (
    <div className="w-full h-[520px] rounded-xl overflow-hidden border border-border bg-[#131722] relative">
      <iframe
        title="TradingView Live Stream Chart"
        src={iframeSrc}
        className="w-full h-full border-0"
        
        scrolling="no"
      />
    </div>
  );
}

export const TradingViewLiveChart = memo(TradingViewWidgetComponent);

