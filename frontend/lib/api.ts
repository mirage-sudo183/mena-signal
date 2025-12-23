const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export interface User {
  id: number;
  email: string;
  created_at: string;
}

export interface Source {
  id: number;
  name: string;
  type: "rss" | "api" | "manual";
  url: string;
  enabled: boolean;
  category: string | null;
  created_at: string;
}

export interface FundingDetails {
  round_type: string | null;
  amount_usd: number | null;
  investors: string[] | null;
  geography: string | null;
}

export interface CompanyDetails {
  one_liner: string | null;
  category: string | null;
  stage_hint: string | null;
  geography: string | null;
}

export interface MenaAnalysis {
  fit_score: number;
  mena_summary: string;
  rubric_json: {
    budget_buyer_exists: number;
    localization_arabic_bilingual: number;
    regulatory_friction: number;
    distribution_path: number;
    time_to_revenue: number;
  } | null;
  model_name: string | null;
  created_at: string;
}

export interface Tag {
  id: number;
  name: string;
  color: string | null;
}

export interface Note {
  id: number;
  body: string;
  created_at: string;
  updated_at: string;
}

export interface Item {
  id: number;
  type: "funding" | "company";
  title: string;
  company_name: string | null;
  url: string;
  source_id: number | null;
  source?: Source | null;
  published_at: string | null;
  summary: string | null;
  hidden: boolean;
  created_at: string;
  funding_details: FundingDetails | null;
  company_details: CompanyDetails | null;
  mena_analysis: MenaAnalysis | null;
  is_favorited: boolean;
  tags: Tag[];
  notes: Note[];
}

export interface ItemListResponse {
  items: Item[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || "Request failed");
  }

  return response.json();
}

// Auth
export async function login(email: string, password: string) {
  return fetchWithAuth("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function register(email: string, password: string) {
  return fetchWithAuth("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function logout() {
  return fetchWithAuth("/api/auth/logout", { method: "POST" });
}

export async function getMe(): Promise<User> {
  return fetchWithAuth("/api/auth/me");
}

// Items
export async function getItems(params: Record<string, string> = {}): Promise<Item[]> {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, String(value));
    }
  });
  const response: ItemListResponse = await fetchWithAuth(`/api/items?${searchParams.toString()}`);
  return response.items || [];
}

export async function getItem(id: number): Promise<Item> {
  return fetchWithAuth(`/api/items/${id}`);
}

export async function createItem(data: {
  type: "funding" | "company";
  title: string;
  company_name?: string;
  url: string;
  summary?: string;
  one_liner?: string;
}): Promise<Item> {
  return fetchWithAuth("/api/items", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function hideItem(id: number) {
  return fetchWithAuth(`/api/items/${id}/hide`, { method: "PATCH" });
}

export async function unhideItem(id: number) {
  return fetchWithAuth(`/api/items/${id}/unhide`, { method: "PATCH" });
}

// Favorites
export async function getFavorites(): Promise<Item[]> {
  const response: ItemListResponse = await fetchWithAuth("/api/favorites");
  return response.items || [];
}

export async function addFavorite(itemId: number) {
  return fetchWithAuth(`/api/favorites/${itemId}`, { method: "POST" });
}

export async function removeFavorite(itemId: number) {
  return fetchWithAuth(`/api/favorites/${itemId}`, { method: "DELETE" });
}

// Tags
export async function getTags(): Promise<Tag[]> {
  return fetchWithAuth("/api/tags");
}

export async function createTag(name: string, color?: string): Promise<Tag> {
  return fetchWithAuth("/api/tags", {
    method: "POST",
    body: JSON.stringify({ name, color }),
  });
}

export async function deleteTag(id: number) {
  return fetchWithAuth(`/api/tags/${id}`, { method: "DELETE" });
}

export async function assignTags(itemId: number, tagIds: number[]) {
  return fetchWithAuth(`/api/tags/items/${itemId}`, {
    method: "POST",
    body: JSON.stringify({ tag_ids: tagIds }),
  });
}

// Notes
export async function addNote(itemId: number, body: string): Promise<Note> {
  return fetchWithAuth(`/api/notes/items/${itemId}`, {
    method: "POST",
    body: JSON.stringify({ body }),
  });
}

export async function updateNote(noteId: number, body: string): Promise<Note> {
  return fetchWithAuth(`/api/notes/${noteId}`, {
    method: "PATCH",
    body: JSON.stringify({ body }),
  });
}

export async function deleteNote(noteId: number) {
  return fetchWithAuth(`/api/notes/${noteId}`, { method: "DELETE" });
}

// Sources
export async function getSources(): Promise<Source[]> {
  return fetchWithAuth("/api/sources");
}

export async function createSource(data: {
  name: string;
  type?: "rss" | "api" | "manual";
  url: string;
  category?: string;
  enabled?: boolean;
}): Promise<Source> {
  return fetchWithAuth("/api/sources", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateSource(
  id: number,
  data: { name?: string; url?: string; enabled?: boolean; category?: string }
): Promise<Source> {
  return fetchWithAuth(`/api/sources/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function toggleSource(id: number, enabled: boolean): Promise<Source> {
  return updateSource(id, { enabled });
}

export async function deleteSource(id: number) {
  return fetchWithAuth(`/api/sources/${id}`, { method: "DELETE" });
}

// Ingest
export async function triggerIngest(sourceId?: number) {
  const body = sourceId ? { source_id: sourceId } : {};
  return fetchWithAuth("/api/ingest/run", {
    method: "POST",
    body: JSON.stringify(body),
  });
}
