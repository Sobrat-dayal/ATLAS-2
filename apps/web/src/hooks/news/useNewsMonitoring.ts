"use client";

import { useCallback, useEffect, useState } from "react";
import {
  createCustomFeed,
  createDigest,
  createMonitoringRule,
  deleteCustomFeed,
  deleteDigest,
  deleteMonitoringRule,
  executeCustomFeedArticles,
  getAlertMatches,
  getCustomFeeds,
  getDigestHistory,
  getDigests,
  getMonitoringHealth,
  getMonitoringRules,
  previewDigest,
  previewMonitoringRule,
  triggerDigest,
  updateCustomFeed,
  updateDigest,
  updateMonitoringRule,
  validateMonitoringRule,
} from "@/lib/news/api";
import {
  CreateCustomNewsFeedDTO,
  CreateNewsDigestSubscriptionDTO,
  CreateNewsMonitoringRuleDTO,
  CustomNewsFeedDTO,
  MonitoringHealthStatusDTO,
  NewsAlertFeedResponseDTO,
  NewsAlertMatchDTO,
  NewsArticleDTO,
  NewsDigestRunDTO,
  NewsDigestSubscriptionDTO,
  NewsMonitoringRuleDTO,
  NewsRulePreviewRequestDTO,
  NewsRulePreviewResponseDTO,
  NewsRuleValidationRequestDTO,
  NewsRuleValidationResponseDTO,
  UpdateCustomNewsFeedDTO,
  UpdateNewsDigestSubscriptionDTO,
  UpdateNewsMonitoringRuleDTO,
} from "@/lib/news/types";

export type MonitoringSubTab = "RULES" | "CUSTOM_FEEDS" | "ALERTS" | "DIGESTS" | "HEALTH";

export function useNewsMonitoring() {
  const [activeSubTab, setActiveSubTab] = useState<MonitoringSubTab>("RULES");

  // Rules state
  const [rules, setRules] = useState<NewsMonitoringRuleDTO[]>([]);
  const [selectedRule, setSelectedRule] = useState<NewsMonitoringRuleDTO | null>(null);
  const [isRulesLoading, setIsRulesLoading] = useState<boolean>(false);

  // Custom feeds state
  const [customFeeds, setCustomFeeds] = useState<CustomNewsFeedDTO[]>([]);
  const [selectedFeed, setSelectedFeed] = useState<CustomNewsFeedDTO | null>(null);
  const [feedArticles, setFeedArticles] = useState<NewsArticleDTO[]>([]);
  const [isFeedsLoading, setIsFeedsLoading] = useState<boolean>(false);

  // Alerts state
  const [alertFeed, setAlertFeed] = useState<NewsAlertFeedResponseDTO | null>(null);
  const [selectedAlert, setSelectedAlert] = useState<NewsAlertMatchDTO | null>(null);
  const [alertFilterStatus, setAlertFilterStatus] = useState<string>("");
  const [alertFilterPriority, setAlertFilterPriority] = useState<string>("");
  const [isAlertsLoading, setIsAlertsLoading] = useState<boolean>(false);

  // Digests state
  const [digests, setDigests] = useState<NewsDigestSubscriptionDTO[]>([]);
  const [selectedDigest, setSelectedDigest] = useState<NewsDigestSubscriptionDTO | null>(null);
  const [digestPreview, setDigestPreview] = useState<NewsDigestRunDTO | null>(null);
  const [digestHistory, setDigestHistory] = useState<NewsDigestRunDTO[]>([]);
  const [isDigestsLoading, setIsDigestsLoading] = useState<boolean>(false);

  // Health state
  const [health, setHealth] = useState<MonitoringHealthStatusDTO | null>(null);
  const [isHealthLoading, setIsHealthLoading] = useState<boolean>(false);

  // Global error
  const [error, setError] = useState<string | null>(null);

  // --------------------------------------------------------------------------
  // Fetch Functions
  // --------------------------------------------------------------------------

  const fetchRules = useCallback(async () => {
    setIsRulesLoading(true);
    try {
      const data = await getMonitoringRules();
      setRules(data);
      if (data.length > 0 && !selectedRule) {
        setSelectedRule(data[0]);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load monitoring rules";
      setError(msg);
    } finally {
      setIsRulesLoading(false);
    }
  }, [selectedRule]);

  const fetchCustomFeeds = useCallback(async () => {
    setIsFeedsLoading(true);
    try {
      const data = await getCustomFeeds();
      setCustomFeeds(data);
      if (data.length > 0 && !selectedFeed) {
        setSelectedFeed(data[0]);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load custom feeds";
      setError(msg);
    } finally {
      setIsFeedsLoading(false);
    }
  }, [selectedFeed]);

  const fetchAlerts = useCallback(async () => {
    setIsAlertsLoading(true);
    try {
      const data = await getAlertMatches({
        match_status: alertFilterStatus || undefined,
        priority: alertFilterPriority || undefined,
        limit: 50,
      });
      setAlertFeed(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load alerts feed";
      setError(msg);
    } finally {
      setIsAlertsLoading(false);
    }
  }, [alertFilterStatus, alertFilterPriority]);

  const fetchDigests = useCallback(async () => {
    setIsDigestsLoading(true);
    try {
      const data = await getDigests();
      setDigests(data);
      if (data.length > 0 && !selectedDigest) {
        setSelectedDigest(data[0]);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load digests";
      setError(msg);
    } finally {
      setIsDigestsLoading(false);
    }
  }, [selectedDigest]);

  const fetchHealth = useCallback(async () => {
    setIsHealthLoading(true);
    try {
      const data = await getMonitoringHealth();
      setHealth(data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to load health status";
      setError(msg);
    } finally {
      setIsHealthLoading(false);
    }
  }, []);

  const refreshAll = useCallback(async () => {
    setError(null);
    await Promise.allSettled([
      fetchRules(),
      fetchCustomFeeds(),
      fetchAlerts(),
      fetchDigests(),
      fetchHealth(),
    ]);
  }, [fetchRules, fetchCustomFeeds, fetchAlerts, fetchDigests, fetchHealth]);

  // Initial load
  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  // Re-fetch alerts on filter change
  useEffect(() => {
    fetchAlerts();
  }, [fetchAlerts]);

  // --------------------------------------------------------------------------
  // Rule Actions
  // --------------------------------------------------------------------------

  const handleCreateRule = async (dto: CreateNewsMonitoringRuleDTO): Promise<NewsMonitoringRuleDTO> => {
    const created = await createMonitoringRule(dto);
    await fetchRules();
    await fetchHealth();
    setSelectedRule(created);
    return created;
  };

  const handleUpdateRule = async (
    ruleId: string,
    dto: UpdateNewsMonitoringRuleDTO
  ): Promise<NewsMonitoringRuleDTO> => {
    const updated = await updateMonitoringRule(ruleId, dto);
    await fetchRules();
    if (selectedRule?.rule_id === ruleId) {
      setSelectedRule(updated);
    }
    return updated;
  };

  const handleToggleRuleActive = async (rule: NewsMonitoringRuleDTO): Promise<void> => {
    await handleUpdateRule(rule.rule_id, { is_active: !rule.is_active });
    await fetchHealth();
  };

  const handleDeleteRule = async (ruleId: string): Promise<void> => {
    await deleteMonitoringRule(ruleId);
    await fetchRules();
    await fetchHealth();
    if (selectedRule?.rule_id === ruleId) {
      setSelectedRule(null);
    }
  };

  const handleValidateRule = async (
    req: NewsRuleValidationRequestDTO
  ): Promise<NewsRuleValidationResponseDTO> => {
    return validateMonitoringRule(req);
  };

  const handlePreviewRule = async (
    req: NewsRulePreviewRequestDTO
  ): Promise<NewsRulePreviewResponseDTO> => {
    return previewMonitoringRule(req);
  };

  // --------------------------------------------------------------------------
  // Custom Feed Actions
  // --------------------------------------------------------------------------

  const handleCreateCustomFeed = async (
    dto: CreateCustomNewsFeedDTO
  ): Promise<CustomNewsFeedDTO> => {
    const created = await createCustomFeed(dto);
    await fetchCustomFeeds();
    await fetchHealth();
    setSelectedFeed(created);
    return created;
  };

  const handleUpdateCustomFeed = async (
    feedId: string,
    dto: UpdateCustomNewsFeedDTO
  ): Promise<CustomNewsFeedDTO> => {
    const updated = await updateCustomFeed(feedId, dto);
    await fetchCustomFeeds();
    if (selectedFeed?.feed_id === feedId) {
      setSelectedFeed(updated);
    }
    return updated;
  };

  const handleDeleteCustomFeed = async (feedId: string): Promise<void> => {
    await deleteCustomFeed(feedId);
    await fetchCustomFeeds();
    await fetchHealth();
    if (selectedFeed?.feed_id === feedId) {
      setSelectedFeed(null);
      setFeedArticles([]);
    }
  };

  const handleExecuteFeed = async (feedId: string): Promise<void> => {
    try {
      const res = await executeCustomFeedArticles(feedId, 25);
      setFeedArticles(res.articles);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to execute custom feed";
      setError(msg);
    }
  };

  // --------------------------------------------------------------------------
  // Digest Actions
  // --------------------------------------------------------------------------

  const handleCreateDigest = async (
    dto: CreateNewsDigestSubscriptionDTO
  ): Promise<NewsDigestSubscriptionDTO> => {
    const created = await createDigest(dto);
    await fetchDigests();
    await fetchHealth();
    setSelectedDigest(created);
    return created;
  };

  const handleUpdateDigest = async (
    digestId: string,
    dto: UpdateNewsDigestSubscriptionDTO
  ): Promise<NewsDigestSubscriptionDTO> => {
    const updated = await updateDigest(digestId, dto);
    await fetchDigests();
    if (selectedDigest?.digest_id === digestId) {
      setSelectedDigest(updated);
    }
    return updated;
  };

  const handleDeleteDigest = async (digestId: string): Promise<void> => {
    await deleteDigest(digestId);
    await fetchDigests();
    await fetchHealth();
    if (selectedDigest?.digest_id === digestId) {
      setSelectedDigest(null);
      setDigestPreview(null);
      setDigestHistory([]);
    }
  };

  const handlePreviewDigest = async (digestId: string): Promise<NewsDigestRunDTO> => {
    const preview = await previewDigest(digestId);
    setDigestPreview(preview);
    return preview;
  };

  const handleTriggerDigest = async (digestId: string): Promise<NewsDigestRunDTO> => {
    const run = await triggerDigest(digestId);
    await fetchDigests();
    await handleLoadDigestHistory(digestId);
    return run;
  };

  const handleLoadDigestHistory = async (digestId: string): Promise<void> => {
    try {
      const history = await getDigestHistory(digestId, 10);
      setDigestHistory(history);
    } catch {
      // Non-blocking history load
    }
  };

  return {
    activeSubTab,
    setActiveSubTab,
    // Rules
    rules,
    selectedRule,
    setSelectedRule,
    isRulesLoading,
    handleCreateRule,
    handleUpdateRule,
    handleToggleRuleActive,
    handleDeleteRule,
    handleValidateRule,
    handlePreviewRule,
    // Feeds
    customFeeds,
    selectedFeed,
    setSelectedFeed,
    feedArticles,
    isFeedsLoading,
    handleCreateCustomFeed,
    handleUpdateCustomFeed,
    handleDeleteCustomFeed,
    handleExecuteFeed,
    // Alerts
    alertFeed,
    selectedAlert,
    setSelectedAlert,
    alertFilterStatus,
    setAlertFilterStatus,
    alertFilterPriority,
    setAlertFilterPriority,
    isAlertsLoading,
    // Digests
    digests,
    selectedDigest,
    setSelectedDigest,
    digestPreview,
    digestHistory,
    isDigestsLoading,
    handleCreateDigest,
    handleUpdateDigest,
    handleDeleteDigest,
    handlePreviewDigest,
    handleTriggerDigest,
    handleLoadDigestHistory,
    // Health
    health,
    isHealthLoading,
    // Global
    error,
    refreshAll,
  };
}
