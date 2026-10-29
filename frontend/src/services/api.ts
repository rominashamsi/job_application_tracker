
const API_BASE_URL = 'http://127.0.0.1:8000'

export type ApiJobStatus = 'applied' | 'interview' | 'offer' | 'rejected'

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface RegisterResponse {
  id: number
  name: string
  email: string
}

export interface ApiJobApplication {
  id: number
  company: string
  job_title: string
  status: ApiJobStatus
  applied_date: string
  job_url: string | null
  notes: string | null
  salary: number | null
}

export interface CreateJobApplicationInput {
  company: string
  job_title: string
  job_url?: string | null
  notes?: string | null
  salary?: number | null
}

async function readErrorMessage(
  response: Response,
  fallback: string,
): Promise<string> {
  try {
    const data: { detail?: unknown } = await response.json()

    if (typeof data.detail === 'string') {
      return data.detail
    }

    if (Array.isArray(data.detail)) {
      const messages = data.detail
        .map((item: { msg?: string }) => item.msg)
        .filter((message): message is string => Boolean(message))

      if (messages.length > 0) {
        return messages.join(', ')
      }
    }
  } catch {
    // Use the fallback when the response is not valid JSON.
  }

  return fallback
}

export async function login(
  email: string,
  password: string,
): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  })

  if (!response.ok) {
    throw new Error(
      await readErrorMessage(response, 'Login failed'),
    )
  }

  return response.json() as Promise<LoginResponse>
}

export async function register(
  name: string,
  email: string,
  password: string,
): Promise<RegisterResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: name.trim(),
      email: email.trim(),
      password,
    }),
  })

  if (!response.ok) {
    throw new Error(
      await readErrorMessage(response, 'Could not create your account'),
    )
  }

  return response.json() as Promise<RegisterResponse>
}

export async function getJobApplications(
  token: string,
): Promise<ApiJobApplication[]> {
  const response = await fetch(`${API_BASE_URL}/job-applications/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error(
      await readErrorMessage(response, 'Could not load applications'),
    )
  }

  return response.json() as Promise<ApiJobApplication[]>
}

export async function createJobApplication(
  token: string,
  application: CreateJobApplicationInput,
): Promise<ApiJobApplication> {
  const response = await fetch(`${API_BASE_URL}/job-applications/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(application),
  })

  if (!response.ok) {
    throw new Error(
      await readErrorMessage(response, 'Could not save the application'),
    )
  }

  return response.json() as Promise<ApiJobApplication>
}


export interface UpdateJobApplicationInput {
  company?: string
  job_title?: string
  status?: ApiJobStatus
  job_url?: string | null
  notes?: string | null
  salary?: number | null
}

export async function updateJobApplication(
  token: string,
  id: number,
  application: UpdateJobApplicationInput,
): Promise<ApiJobApplication> {
  const response = await fetch(
    `${API_BASE_URL}/job-applications/${id}`,
    {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(application),
    },
  )

  if (!response.ok) {
    throw new Error(
      await readErrorMessage(
        response,
        'Could not update the application.',
      ),
    )
  }

  return response.json()
}


export async function deleteJobApplication(
  token: string,
  id: number,
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/job-applications/${id}`,
    {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  )

  if (!response.ok) {
    throw new Error(
      await readErrorMessage(response, 'Could not delete the application'),
    )
  }
}
