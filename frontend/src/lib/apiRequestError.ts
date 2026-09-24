export class ApiRequestError extends Error {
  constructor(message: string, public status: number, public code?: string) { super(message); }
}

export async function apiRequestError(response: Response): Promise<ApiRequestError> {
  const payload = await response.json().catch(() => null);
  const detail = payload?.detail && typeof payload.detail === 'object' ? payload.detail : payload;
  if (response.status === 409 && detail?.code === 'onboarding_required') {
    return new ApiRequestError('Finish your style profile and ten-item capsule before creating a new outfit.', 409, 'onboarding_required');
  }
  const message = typeof payload?.error === 'string' ? payload.error : typeof payload?.detail === 'string' ? payload.detail : `We could not complete the request (${response.status}). Please try again.`;
  return new ApiRequestError(message, response.status);
}

export function isOnboardingRequired(error: unknown): error is ApiRequestError {
  return error instanceof ApiRequestError && error.code === 'onboarding_required';
}
