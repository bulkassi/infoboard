const API_BASE = import.meta.env.VITE_API_URL || ''
const API_PREFIX = '/api/v1'

export class ApiError extends Error {
  constructor(message, status, payload) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.payload = payload
  }
}

export function buildApiUrl(path) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${API_BASE}${API_PREFIX}${normalizedPath}`
}

export function buildFileUrl(fileId) {
  if (!Number.isInteger(fileId)) {
    return ''
  }
  return buildApiUrl(`/files/${fileId}`)
}

async function parseErrorPayload(response) {
  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    try {
      return await response.json()
    } catch {
      return null
    }
  }
  try {
    return await response.text()
  } catch {
    return null
  }
}

function resolveErrorMessage(payload, fallback) {
  if (!payload) {
    return fallback
  }

  if (typeof payload === 'string' && payload.trim()) {
    return payload
  }

  if (typeof payload === 'object' && payload.detail) {
    return String(payload.detail)
  }

  return fallback
}

export async function apiRequest(
  path,
  { method = 'GET', body, form, token, headers = {}, signal } = {},
) {
  const requestHeaders = new Headers(headers)
  const options = {
    method,
    headers: requestHeaders,
    credentials: 'include',
    signal,
  }

  if (token) {
    requestHeaders.set('Authorization', `Bearer ${token}`)
  }

  if (form) {
    const params = new URLSearchParams()
    Object.entries(form).forEach(([key, value]) => {
      if (value === undefined || value === null) {
        return
      }
      params.append(key, String(value))
    })
    options.body = params
    requestHeaders.set('Content-Type', 'application/x-www-form-urlencoded')
  } else if (body instanceof FormData) {
    options.body = body
  } else if (body !== undefined) {
    options.body = JSON.stringify(body)
    requestHeaders.set('Content-Type', 'application/json')
  }

  const response = await fetch(buildApiUrl(path), options)
  if (!response.ok) {
    const payload = await parseErrorPayload(response)
    const message = resolveErrorMessage(payload, `Request failed with ${response.status}`)
    throw new ApiError(message, response.status, payload)
  }

  if (response.status === 204) {
    return null
  }

  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    return response.json()
  }

  return response.text()
}
