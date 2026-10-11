"use client";

import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { useAuth } from "@/hooks/auth/useAuth";
import {
  archiveNotification,
  getUnreadNotificationCount,
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  markNotificationUnread,
} from "./client";
import { UNREAD_COUNT_POLL_INTERVAL_MS } from "./constants";
import { NotificationItem, NotificationListFilter } from "./types";

export interface NotificationsContextValue {
  items: NotificationItem[];
  unreadCount: number;
  filter: NotificationListFilter;
  setFilter: (filter: NotificationListFilter) => void;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  isLoading: boolean;
  isLoadingMore: boolean;
  hasMore: boolean;
  error: string | null;
  loadMore: () => Promise<void>;
  refreshList: () => Promise<void>;
  refreshUnreadCount: () => Promise<void>;
  markRead: (id: string) => Promise<void>;
  markUnread: (id: string) => Promise<void>;
  archive: (id: string) => Promise<void>;
  markAllRead: () => Promise<void>;
}

const NotificationsContext = createContext<NotificationsContextValue | null>(null);

export function NotificationsProvider({ children }: { children: React.ReactNode }) {
  const { session } = useAuth();
  const token = session?.access_token || null;
  const userId = session?.user?.id || null;

  const [isOpen, setIsOpen] = useState(false);
  const [filter, setFilter] = useState<NotificationListFilter>("all");
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const prevUserIdRef = useRef<string | null>(userId);

  // 1. Auth principal change / logout isolation: clear all memory state
  useEffect(() => {
    if (prevUserIdRef.current !== userId) {
      prevUserIdRef.current = userId;
      setItems([]);
      setUnreadCount(0);
      setNextCursor(null);
      setHasMore(false);
      setError(null);
      setIsOpen(false);
    }
  }, [userId]);

  // 2. Fetch unread count
  const refreshUnreadCount = useCallback(async () => {
    if (!token) {
      setUnreadCount(0);
      return;
    }
    try {
      const res = await getUnreadNotificationCount({ token });
      setUnreadCount(Math.max(0, res.unread_count));
    } catch {
      // Bounded retry via polling interval
    }
  }, [token]);

  // 3. Fetch notifications list
  const refreshList = useCallback(async () => {
    if (!token) {
      setItems([]);
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const res = await listNotifications(
        { filter, limit: 25, cursor: null },
        { token }
      );
      setItems(res.items);
      setNextCursor(res.next_cursor);
      setHasMore(res.has_more);
      if (typeof res.unread_count === "number") {
        setUnreadCount(Math.max(0, res.unread_count));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load notifications");
    } finally {
      setIsLoading(false);
    }
  }, [token, filter]);

  // 4. Load more via deterministic keyset cursor
  const loadMore = useCallback(async () => {
    if (!token || !nextCursor || isLoadingMore || !hasMore) return;
    setIsLoadingMore(true);
    try {
      const res = await listNotifications(
        { filter, limit: 25, cursor: nextCursor },
        { token }
      );
      setItems((prev) => [...prev, ...res.items]);
      setNextCursor(res.next_cursor);
      setHasMore(res.has_more);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load more notifications");
    } finally {
      setIsLoadingMore(false);
    }
  }, [token, filter, nextCursor, isLoadingMore, hasMore]);

  // 5. Unread count polling: 30s while authenticated & document visible
  useEffect(() => {
    if (!token) return;

    let cancelled = false;
    const fetchCount = async () => {
      try {
        const res = await getUnreadNotificationCount({ token });
        if (!cancelled) setUnreadCount(Math.max(0, res.unread_count));
      } catch {
        // Bounded retry via polling interval
      }
    };

    fetchCount();

    const intervalId = setInterval(() => {
      if (typeof document !== "undefined" && document.visibilityState === "visible") {
        fetchCount();
      }
    }, UNREAD_COUNT_POLL_INTERVAL_MS);

    const onVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        fetchCount();
      }
    };

    const onFocus = () => {
      fetchCount();
    };

    window.addEventListener("visibilitychange", onVisibilityChange);
    window.addEventListener("focus", onFocus);

    return () => {
      cancelled = true;
      clearInterval(intervalId);
      window.removeEventListener("visibilitychange", onVisibilityChange);
      window.removeEventListener("focus", onFocus);
    };
  }, [token]);

  // 6. When Notification Center opens or filter changes: refetch list & unread count
  useEffect(() => {
    if (!isOpen || !token) return;

    let cancelled = false;
    const fetchListAndCount = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const [listRes, countRes] = await Promise.all([
          listNotifications({ filter, limit: 25, cursor: null }, { token }),
          getUnreadNotificationCount({ token }),
        ]);
        if (!cancelled) {
          setItems(listRes.items);
          setNextCursor(listRes.next_cursor);
          setHasMore(listRes.has_more);
          setUnreadCount(Math.max(0, countRes.unread_count));
        }
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load notifications");
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    fetchListAndCount();

    return () => {
      cancelled = true;
    };
  }, [isOpen, filter, token]);

  // 7. Optimistic Mutations
  const markRead = useCallback(
    async (id: string) => {
      if (!token) return;

      const previousItems = [...items];
      const previousCount = unreadCount;
      const target = items.find((i) => i.notification_id === id);
      const wasUnread = target && !target.read_at && !target.archived_at;

      // Optimistic update
      setItems((prev) =>
        prev.map((item) =>
          item.notification_id === id
            ? { ...item, read_at: new Date().toISOString() }
            : item
        )
      );
      if (wasUnread) {
        setUnreadCount((c) => Math.max(0, c - 1));
      }

      try {
        await markNotificationRead(id, { token });
      } catch {
        // Rollback
        setItems(previousItems);
        setUnreadCount(previousCount);
        setError("Failed to mark notification as read.");
      }
    },
    [token, items, unreadCount]
  );

  const markUnread = useCallback(
    async (id: string) => {
      if (!token) return;

      const previousItems = [...items];
      const previousCount = unreadCount;
      const target = items.find((i) => i.notification_id === id);
      const wasRead = target && target.read_at && !target.archived_at;

      // Optimistic update
      setItems((prev) =>
        prev.map((item) =>
          item.notification_id === id ? { ...item, read_at: null } : item
        )
      );
      if (wasRead) {
        setUnreadCount((c) => c + 1);
      }

      try {
        await markNotificationUnread(id, { token });
      } catch {
        // Rollback
        setItems(previousItems);
        setUnreadCount(previousCount);
        setError("Failed to mark notification as unread.");
      }
    },
    [token, items, unreadCount]
  );

  const archive = useCallback(
    async (id: string) => {
      if (!token) return;

      const previousItems = [...items];
      const previousCount = unreadCount;
      const target = items.find((i) => i.notification_id === id);
      const wasUnread = target && !target.read_at && !target.archived_at;

      // Optimistic update: remove from active center list
      setItems((prev) => prev.filter((i) => i.notification_id !== id));
      if (wasUnread) {
        setUnreadCount((c) => Math.max(0, c - 1));
      }

      try {
        await archiveNotification(id, { token });
      } catch {
        // Rollback
        setItems(previousItems);
        setUnreadCount(previousCount);
        setError("Failed to archive notification.");
      }
    },
    [token, items, unreadCount]
  );

  const markAllRead = useCallback(async () => {
    if (!token) return;

    const previousItems = [...items];
    const previousCount = unreadCount;

    // Optimistic update
    const nowIso = new Date().toISOString();
    setItems((prev) =>
      prev.map((i) => (!i.read_at ? { ...i, read_at: nowIso } : i))
    );
    setUnreadCount(0);

    try {
      await markAllNotificationsRead({ token });
    } catch {
      // Rollback
      setItems(previousItems);
      setUnreadCount(previousCount);
      setError("Failed to mark all notifications as read.");
    }
  }, [token, items, unreadCount]);

  return (
    <NotificationsContext.Provider
      value={{
        items,
        unreadCount,
        filter,
        setFilter,
        isOpen,
        setIsOpen,
        isLoading,
        isLoadingMore,
        hasMore,
        error,
        loadMore,
        refreshList,
        refreshUnreadCount,
        markRead,
        markUnread,
        archive,
        markAllRead,
      }}
    >
      {children}
    </NotificationsContext.Provider>
  );
}

export function useNotifications(): NotificationsContextValue {
  const ctx = useContext(NotificationsContext);
  if (!ctx) {
    throw new Error("useNotifications must be used within a NotificationsProvider");
  }
  return ctx;
}
