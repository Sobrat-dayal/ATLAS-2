export function MarketTickerBar() {
  // Demo fixture data for Stage 3 (External data source placeholder)
  const tickers = [
    { symbol: "S&P 500", price: "5,137.08", change: "+0.42%", positive: true },
    { symbol: "NASDAQ", price: "16,274.94", change: "+0.67%", positive: true },
    { symbol: "DOW", price: "38,901.02", change: "+0.31%", positive: true },
    { symbol: "NIFTY", price: "22,147.30", change: "-0.18%", positive: false },
    { symbol: "BTC", price: "67,230.40", change: "+1.24%", positive: true },
    { symbol: "EUR/USD", price: "1.0841", change: "-0.05%", positive: false },
    { symbol: "GOLD", price: "2,082.30", change: "+0.85%", positive: true },
    { symbol: "US10Y", price: "4.18%", change: "-0.02", positive: false },
  ];

  return (
    <div className="flex h-7 w-full items-center overflow-x-auto overflow-y-hidden border-b border-[#1E2330] bg-[#0A0D14] px-2 text-[11px] font-mono whitespace-nowrap custom-scrollbar">
      {tickers.map((ticker, index) => (
        <div key={ticker.symbol} className="flex items-center px-4 flex-shrink-0">
          <span className="font-semibold text-gray-300 mr-2">{ticker.symbol}</span>
          <span className="text-white mr-2">{ticker.price}</span>
          <span className={ticker.positive ? "text-green-400" : "text-red-400"}>
            {ticker.change}
          </span>
          {index < tickers.length - 1 && (
            <div className="ml-4 h-3 w-px bg-[#1E2330]"></div>
          )}
        </div>
      ))}
    </div>
  );
}
