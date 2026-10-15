"use client";

import { useCallback, useState } from "react";
import { useAuth } from "@/hooks/auth";
import {
  convertFxCurrency,
  FxConversionMode,
  FxConversionResponse,
} from "@/lib/markets/fx";

export interface UseFxConversionOptions {
  initialAmount?: string;
  initialFromCurrency?: string;
  initialToCurrency?: string;
  initialMode?: FxConversionMode;
}

export interface UseFxConversionResult {
  amount: string;
  setAmount: (a: string) => void;
  fromCurrency: string;
  setFromCurrency: (c: string) => void;
  toCurrency: string;
  setToCurrency: (c: string) => void;
  mode: FxConversionMode;
  setMode: (m: FxConversionMode) => void;

  result: FxConversionResponse | null;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;

  convert: () => Promise<void>;
  swapCurrencies: () => Promise<void>;
  reset: () => void;
}

export function useFxConversion(
  options?: UseFxConversionOptions
): UseFxConversionResult {
  const { session } = useAuth();
  const token = session?.access_token || null;

  const [amount, setAmount] = useState<string>(options?.initialAmount || "100");
  const [fromCurrency, setFromCurrency] = useState<string>(
    options?.initialFromCurrency || "EUR"
  );
  const [toCurrency, setToCurrency] = useState<string>(
    options?.initialToCurrency || "USD"
  );
  const [mode, setMode] = useState<FxConversionMode>(
    options?.initialMode || "INDICATIVE_MID"
  );

  const [result, setResult] = useState<FxConversionResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isError, setIsError] = useState<boolean>(false);
  const [error, setError] = useState<Error | null>(null);

  const executeConversion = useCallback(
    async (fromCcy: string, toCcy: string, amt: string, m: FxConversionMode) => {
      const numAmt = parseFloat(amt);
      if (isNaN(numAmt) || numAmt <= 0) {
        setIsError(true);
        setError(new Error("Please enter a valid positive conversion amount."));
        return;
      }

      setIsLoading(true);
      setIsError(false);
      setError(null);

      try {
        const res = await convertFxCurrency(
          {
            amount: amt.trim(),
            from_currency: fromCcy.trim().toUpperCase(),
            to_currency: toCcy.trim().toUpperCase(),
            mode: m,
          },
          { token }
        );
        setResult(res);
      } catch (err) {
        setIsError(true);
        setResult(null);
        setError(err instanceof Error ? err : new Error(String(err)));
      } finally {
        setIsLoading(false);
      }
    },
    [token]
  );

  const convert = useCallback(async () => {
    await executeConversion(fromCurrency, toCurrency, amount, mode);
  }, [executeConversion, fromCurrency, toCurrency, amount, mode]);

  const swapCurrencies = useCallback(async () => {
    const nextFrom = toCurrency;
    const nextTo = fromCurrency;
    setFromCurrency(nextFrom);
    setToCurrency(nextTo);
    await executeConversion(nextFrom, nextTo, amount, mode);
  }, [toCurrency, fromCurrency, amount, mode, executeConversion]);

  const reset = useCallback(() => {
    setAmount("100");
    setFromCurrency("EUR");
    setToCurrency("USD");
    setMode("INDICATIVE_MID");
    setResult(null);
    setIsError(false);
    setError(null);
  }, []);

  return {
    amount,
    setAmount,
    fromCurrency,
    setFromCurrency,
    toCurrency,
    setToCurrency,
    mode,
    setMode,
    result,
    isLoading,
    isError,
    error,
    convert,
    swapCurrencies,
    reset,
  };
}
