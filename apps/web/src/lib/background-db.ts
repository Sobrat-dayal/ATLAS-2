import { AtlasBackgroundAsset } from "@/hooks/background/types";

const DB_NAME = "atlas-assets";
const DB_VERSION = 1;
const STORE_NAME = "backgrounds";

interface AssetRecord extends AtlasBackgroundAsset {
  blob: Blob;
  thumbnail?: Blob;
}

let dbPromise: Promise<IDBDatabase> | null = null;

function getDb(): Promise<IDBDatabase> {
  if (typeof window === "undefined") return Promise.reject("IndexedDB not available on server");
  if (!dbPromise) {
    dbPromise = new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME, { keyPath: "id" });
        }
      };
    });
  }
  return dbPromise;
}

export async function saveBackgroundAsset(asset: AtlasBackgroundAsset, blob: Blob, thumbnail?: Blob): Promise<void> {
  const db = await getDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readwrite");
    const store = tx.objectStore(STORE_NAME);
    const record: AssetRecord = { ...asset, blob, thumbnail };
    const request = store.put(record);
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
}

export async function getBackgroundAsset(id: string): Promise<AssetRecord | null> {
  const db = await getDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readonly");
    const store = tx.objectStore(STORE_NAME);
    const request = store.get(id);
    request.onsuccess = () => resolve(request.result || null);
    request.onerror = () => reject(request.error);
  });
}

export async function listBackgroundAssets(): Promise<AtlasBackgroundAsset[]> {
  const db = await getDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readonly");
    const store = tx.objectStore(STORE_NAME);
    const request = store.getAll();
    request.onsuccess = () => {
      // Exclude blob and thumbnail to save memory when listing
      const assets = request.result.map((record: AssetRecord) => {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const { blob, thumbnail, ...meta } = record;
        return meta;
      });
      // Sort newest first
      resolve(assets.sort((a, b) => b.createdAt - a.createdAt));
    };
    request.onerror = () => reject(request.error);
  });
}

export async function deleteBackgroundAsset(id: string): Promise<void> {
  const db = await getDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readwrite");
    const store = tx.objectStore(STORE_NAME);
    const request = store.delete(id);
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
}
