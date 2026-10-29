
<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  login,
  register,
  getJobApplications,
  createJobApplication,
  updateJobApplication,
  deleteJobApplication,
  type ApiJobApplication,
} from './services/api'

import { onMounted } from 'vue'


type JobStatus = 'Applied' | 'Interview' | 'Offer' | 'Rejected'
type FilterStatus = 'All' | JobStatus
type AuthMode = 'login' | 'register'

interface JobApplication {
  id: number
  company: string
  jobTitle: string
  status: JobStatus
  appliedDate: string
  jobUrl: string | null
  salary: number | null
  notes: string | null
}

const statusToApi: Record<JobStatus, ApiJobApplication['status']> = {
  Applied: 'applied',
  Interview: 'interview',
  Offer: 'offer',
  Rejected: 'rejected',
}

const applications = ref<JobApplication[]>([])

const sortOrder = ref<'newest' | 'oldest'>('newest')
const applicationToDelete = ref<JobApplication | null>(null)
const isDeletingApplication = ref(false)
const authMode = ref<AuthMode>('login')
const name = ref('')
const email = ref('')
const password = ref('')
const accessToken = ref(localStorage.getItem('accessToken') ?? '')
const isAuthenticated = ref(false)
const isCheckingSession = ref(true)
const isLoggingIn = ref(false)
const loginError = ref('')
const authSuccess = ref('')
const activeSection = ref<'dashboard' | 'applications'>('dashboard')
const company = ref('')
const jobTitle = ref('')
const editingId = ref<number | null>(null)
const jobUrl = ref('')
const salary = ref('')
const notes = ref('')
const selectedStatus = ref<FilterStatus>('All')
const searchQuery = ref('')
const errorMessage = ref('')
const actionError = ref('')
const isSavingApplication = ref(false)
const updatingIds = ref<number[]>([])
const deletingIds = ref<number[]>([])


const filteredApplications = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()

  return applications.value
    .filter((application) => {
      const matchesStatus =
        selectedStatus.value === 'All' ||
        application.status === selectedStatus.value

      const matchesSearch =
        application.company.toLowerCase().includes(query) ||
        application.jobTitle.toLowerCase().includes(query)

      return matchesStatus && matchesSearch
    })
    .sort((a, b) => {
      return (
        new Date(b.appliedDate).getTime() -
        new Date(a.appliedDate).getTime()
      )
    })
})


const totalApplications = computed(() => applications.value.length)

const appliedCount = computed(
  () => applications.value.filter((item) => item.status === 'Applied').length,
)

const interviewCount = computed(
  () => applications.value.filter((item) => item.status === 'Interview').length,
)

const offerCount = computed(
  () => applications.value.filter((item) => item.status === 'Offer').length,
)
const rejectedCount = computed(
  () => applications.value.filter((item) => item.status === 'Rejected').length,
)



onMounted(async () => {
  const token = localStorage.getItem('accessToken')

  if (!token) {
    isCheckingSession.value = false
    return
  }

  try {
    const response = await fetch('http://127.0.0.1:8000/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      throw new Error('Session expired')
    }

    const user = await response.json()
    const data = await getJobApplications(token)

    accessToken.value = token
    email.value = user.email
    applications.value = data.map(mapApplication)
    isAuthenticated.value = true
  } catch {
    localStorage.removeItem('accessToken')
    accessToken.value = ''
    applications.value = []
    isAuthenticated.value = false
  } finally {
    isCheckingSession.value = false
  }
})



function formatApplicationDate(date: string) {
  const parsedDate = new Date(date)

  if (Number.isNaN(parsedDate.getTime())) {
    return date
  }

  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }).format(parsedDate)
}





function mapApplication(application: ApiJobApplication): JobApplication {
  const statusLabels: Record<ApiJobApplication['status'], JobStatus> = {
    applied: 'Applied',
    interview: 'Interview',
    offer: 'Offer',
    rejected: 'Rejected',
  }

  return {
  id: application.id,
  company: application.company,
  jobTitle: application.job_title,
  status: statusLabels[application.status],
  appliedDate: application.applied_date,
  jobUrl: application.job_url,
  salary: application.salary,
  notes: application.notes,
}
}

function switchAuthMode() {
  authMode.value = authMode.value === 'login' ? 'register' : 'login'
  loginError.value = ''
  authSuccess.value = ''
}

async function handleAuthSubmit() {
  loginError.value = ''
  authSuccess.value = ''
  isLoggingIn.value = true

  try {
    if (authMode.value === 'register') {
      await register(name.value, email.value, password.value)

      authMode.value = 'login'
      name.value = ''
      authSuccess.value =
        'Account created successfully. You can now sign in.'
      return
    }

    const result = await login(email.value.trim(), password.value)
    const data = await getJobApplications(result.access_token)

    accessToken.value = result.access_token
    localStorage.setItem('accessToken', result.access_token)
    applications.value = data.map(mapApplication)
    isAuthenticated.value = true
    password.value = ''
  } catch (error) {
    loginError.value =
      error instanceof Error
        ? error.message
        : 'Something went wrong. Please try again.'
  } finally {
    isLoggingIn.value = false
  }
}

function logout() {
  accessToken.value = ''
  localStorage.removeItem('accessToken')
  applications.value = []
  email.value = ''
  password.value = ''
  name.value = ''
  company.value = ''
  jobTitle.value = ''
  jobUrl.value = ''
  salary.value = ''
  notes.value = ''
  selectedStatus.value = 'All'
  isAuthenticated.value = false
  authMode.value = 'login'
  loginError.value = ''
  authSuccess.value = ''
  errorMessage.value = ''
  actionError.value = ''
}


function editApplication(application: JobApplication) {
  editingId.value = application.id
  company.value = application.company
  jobTitle.value = application.jobTitle
  jobUrl.value = application.jobUrl ?? ''
  salary.value = application.salary?.toString() ?? ''
  notes.value = application.notes ?? ''
  errorMessage.value = ''
}




async function addApplication() {
  errorMessage.value = ''

  if (!company.value.trim() || !jobTitle.value.trim()) {
    errorMessage.value = 'Please enter both company and job title.'
    return
  }

  if (!accessToken.value) {
    errorMessage.value = 'Please sign in again.'
    return
  }

  const salaryText = String(salary.value ?? '').trim()

  const salaryValue =
    salaryText !== '' ? Number(salaryText) : null

  if (
    salaryValue !== null &&
    (!Number.isFinite(salaryValue) || salaryValue < 0)
  ) {
    errorMessage.value = 'Please enter a valid salary.'
    return
  }

  isSavingApplication.value = true

  try {
    const applicationData = {
      company: company.value.trim(),
      job_title: jobTitle.value.trim(),
      job_url: jobUrl.value.trim() || null,
      salary: salaryValue,
      notes: notes.value.trim() || null,
    }

    if (editingId.value !== null) {
      const updatedApplication = await updateJobApplication(
        accessToken.value,
        editingId.value,
        {
          company: applicationData.company,
          job_title: applicationData.job_title,
          job_url: applicationData.job_url,
          salary: applicationData.salary,
          notes: applicationData.notes,
        },
      )

      const index = applications.value.findIndex(
        (item) => item.id === editingId.value,
      )

      if (index !== -1) {
        applications.value[index] = mapApplication(updatedApplication)
      }
    } else {
      const createdApplication = await createJobApplication(
        accessToken.value,
        applicationData,
      )

      applications.value.unshift(mapApplication(createdApplication))
    }

    editingId.value = null
    company.value = ''
    jobTitle.value = ''
    jobUrl.value = ''
    salary.value = ''
    notes.value = ''
    selectedStatus.value = 'All'
  } catch (error) {
    errorMessage.value =
      error instanceof Error
        ? error.message
        : 'Could not save the application.'
  } finally {
    isSavingApplication.value = false
  }
}


async function handleStatusChange(application: JobApplication, event: Event) {
  const select = event.target

  if (!(select instanceof HTMLSelectElement)) {
    return
  }

  const previousStatus = application.status
  const newStatus = select.value as JobStatus

  if (newStatus === previousStatus) {
    return
  }

  actionError.value = ''
  updatingIds.value = [...updatingIds.value, application.id]

  try {
    const updatedApplication = await updateJobApplication(
      accessToken.value,
      application.id,
      {
    status: statusToApi[newStatus],
  },
    )

    const index = applications.value.findIndex(
      (item) => item.id === application.id,
    )

    if (index !== -1) {
      applications.value[index] = mapApplication(updatedApplication)
    }
  } catch (error) {
    select.value = previousStatus
    actionError.value =
      error instanceof Error ? error.message : 'Could not update the status.'
  } finally {
    updatingIds.value = updatingIds.value.filter(
      (id) => id !== application.id,
    )
  }
}


function removeApplication(application: JobApplication) {
  applicationToDelete.value = application
}

async function confirmDeleteApplication() {
  const application = applicationToDelete.value

  if (!application || !accessToken.value) {
    return
  }

  actionError.value = ''
  isDeletingApplication.value = true

  try {
    await deleteJobApplication(accessToken.value, application.id)

    applications.value = applications.value.filter(
      (item) => item.id !== application.id,
    )

    applicationToDelete.value = null
  } catch (error) {
    actionError.value =
      error instanceof Error
        ? error.message
        : 'Could not delete application.'
  } finally {
    isDeletingApplication.value = false
  }
}


</script>

<template>
  <div v-if="isCheckingSession" class="session-loading">
  Loading your workspace...
</div>

<div v-else-if="!isAuthenticated" class="login-page">
    <article class="panel login-panel">
      <div class="brand">
        <span class="brand-icon">CT</span>
        <span>CareerTrack</span>
      </div>

      <p class="eyebrow">YOUR CAREER JOURNEY</p>

      <h1>
        {{ authMode === 'login' ? 'Welcome back' : 'Create your account' }}
      </h1>

      <p class="form-description">
        {{
          authMode === 'login'
            ? 'Sign in to manage your job applications.'
            : 'Create an account to start tracking opportunities.'
        }}
      </p>

      <form @submit.prevent="handleAuthSubmit">
        <template v-if="authMode === 'register'">
          <label for="register-name">Name</label>
          <input
            id="register-name"
            v-model="name"
            type="text"
            autocomplete="name"
            placeholder="Your name"
            minlength="1"
            maxlength="100"
            required
          />
        </template>

        <label for="auth-email">Email</label>
        <input
          id="auth-email"
          v-model="email"
          type="email"
          autocomplete="email"
          placeholder="you@example.com"
          required
        />

        <label for="auth-password">Password</label>
        <input
          id="auth-password"
          v-model="password"
          type="password"
          :autocomplete="authMode === 'register' ? 'new-password' : 'current-password'"
          :placeholder="authMode === 'register' ? 'At least 8 characters' : 'Your password'"
          :minlength="authMode === 'register' ? 8 : undefined"
          maxlength="128"
          required
        />

        <p v-if="authSuccess" class="success-message">
          {{ authSuccess }}
        </p>

        <p v-if="loginError" class="error-message">
          {{ loginError }}
        </p>

        <button type="submit" :disabled="isLoggingIn">
          {{
            isLoggingIn
              ? 'Please wait...'
              : authMode === 'login'
                ? 'Sign in'
                : 'Create account'
          }}
        </button>
      </form>

      <p class="auth-switch-text">
        {{
          authMode === 'login'
            ? "Don't have an account?"
            : 'Already have an account?'
        }}
        <button
          type="button"
          class="auth-switch"
          :disabled="isLoggingIn"
          @click="switchAuthMode"
        >
          {{ authMode === 'login' ? 'Create one' : 'Sign in' }}
        </button>
      </p>
    </article>
  </div>

  <div v-else class="app-layout">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-icon"><img src="/career-track.svg" alt="CareerTrack" /></span>
        <span>CareerTrack</span>
      </div>

      <p class="nav-label">WORKSPACE</p>
      
<button
  type="button"
  class="nav-item"
  :class="{ active: activeSection === 'dashboard' }"
  @click="activeSection = 'dashboard'"
>
  ▦ &nbsp; Dashboard
</button>

<button
  type="button"
  class="nav-item"
  :class="{ active: activeSection === 'applications' }"
  @click="activeSection = 'applications'"
>
  ▤ &nbsp; Applications
</button>


      <div class="sidebar-bottom">
        <div class="avatar">CT</div>
        <div>
          <strong>My Workspace</strong>
          <p>Job seeker</p>
        </div>
      </div>
    </aside>

    <main class="main-content">
      <header class="topbar">
        <span>Workspace / Dashboard</span>

        <div class="topbar-actions">
          <span class="topbar-label">JOB SEARCH WORKSPACE</span>
          <button type="button" class="logout-button" @click="logout">
            Sign out
          </button>
        </div>
      </header>

      <section class="page-heading">
        <div>
          <p class="eyebrow">YOUR CAREER JOURNEY</p>
          <h1>Job applications</h1>
          <p class="subtitle">
            Keep every opportunity organized in one place.
          </p>
        </div>

        <span class="total-badge">
          {{ totalApplications }} applications
        </span>
      </section>

      <section v-if="activeSection === 'dashboard'" class="stats-grid">
        <article class="stat-card">
          <p>Total applications</p>
          <strong>{{ totalApplications }}</strong>
          <span>All opportunities</span>
        </article>

        <article class="stat-card">
          <p>Applied</p>
          <strong>{{ appliedCount }}</strong>
          <span>Waiting for a response</span>
        </article>

        <article class="stat-card">
          <p>Interviews</p>
          <strong>{{ interviewCount }}</strong>
          <span>Opportunities in progress</span>
        </article>

        <article class="stat-card">
          <p>Offers</p>
          <strong>{{ offerCount }}</strong>
          <span>Positive outcomes</span>
        </article>

        <article class="stat-card">
          <p>Rejected</p>
          <strong>{{ rejectedCount }}</strong>
          <span>Applications declined</span>
        </article>
      </section>

      <p v-if="actionError" class="error-message action-error">
        {{ actionError }}
      </p>

      <section class="content-grid">
        <article
           v-if="activeSection === 'applications'"
          class="panel"
          >
          <div class="panel-heading">
            <div>
              <h2>Your applications</h2>
              <p>Track your latest opportunities.</p>
            </div>

            <div class="application-filters">
             <input
              v-model="searchQuery"
              type="search"
              placeholder="Search company or job title..."
              aria-label="Search applications"
            />
            <select v-model="selectedStatus" aria-label="Filter by status">
              <option value="All">All statuses</option>
              <option value="Applied">Applied</option>
              <option value="Interview">Interview</option>
              <option value="Offer">Offer</option>
              <option value="Rejected">Rejected</option>
            </select>
          </div>
        </div>
          <div
            v-if="filteredApplications.length > 0"
            class="application-list"
          >
            <article
              v-for="application in filteredApplications"
              :key="application.id"
              class="application-item"
            >
              <div class="company-icon">
                {{ application.company.charAt(0).toUpperCase() }}
              </div>

              <div class="job-info">
                <strong>{{ application.jobTitle }}</strong>
                <span>{{ application.company }}</span>
                <small>{{ formatApplicationDate(application.appliedDate) }}</small>
                
                <a
                  v-if="application.jobUrl"
                  class="job-link"
                  :href="application.jobUrl"
                  target="_blank"
                  rel="noopener noreferrer"
                >View job posting ↗</a>
                <small v-if="application.salary !== null">
                  Salary: {{ application.salary.toLocaleString() }}
                </small>
                <small v-if="application.notes" class="job-notes">
                  {{ application.notes }}
                </small>
              </div>

              <div class="application-actions">
                <span
                  class="status"
                  :class="application.status.toLowerCase()"
                >
                  {{ application.status }}
                </span>

                <label class="status-label">
                  <span>Change status</span>
                  <select
                    :value="application.status"
                    :disabled="updatingIds.includes(application.id)"
                    :aria-label="`Change status for ${application.company}`"
                    @change="handleStatusChange(application, $event)"
                  >
                    <option value="Applied">Applied</option>
                    <option value="Interview">Interview</option>
                    <option value="Offer">Offer</option>
                    <option value="Rejected">Rejected</option>
                  </select>
                </label>
                
               <button
                  type="button"
                  class="edit-button"
                  @click="editApplication(application)"
                >
                  Edit
                </button>

                <button
                  type="button"
                  class="delete-button"
                  :disabled="deletingIds.includes(application.id)"
                  @click="removeApplication(application)"
                >
                  {{
                    deletingIds.includes(application.id)
                      ? 'Deleting...'
                      : 'Delete'
                  }}
                </button>
              </div>
            </article>
          </div>

          <p v-else class="empty-state">
            {{
              selectedStatus === 'All'
                ? 'No applications yet. Add your first opportunity.'
                : 'No applications found for this status.'
            }}
          </p>
        </article>

        <article
  v-if="activeSection === 'applications'"
  class="panel add-panel"
>
          
          <h2>
             {{ editingId !== null ? 'Edit application' : 'Add an application' }}
          </h2>

          <p class="form-description">
            Save a new job opportunity to your tracker.
          </p>

          <form @submit.prevent="addApplication">
            <label for="company">Company</label>
            <input
              id="company"
              v-model="company"
              placeholder="Enter company name"
              maxlength="150"
              required
            />

            <label for="job-title">Job title</label>
            <input
              id="job-title"
              v-model="jobTitle"
              placeholder="e.g. Junior AI Engineer"
              maxlength="150"
              required
            />

            <label for="job-url">Job URL <span class="optional-label">(optional)</span></label>
            <input
              id="job-url"
              v-model="jobUrl"
              type="url"
              placeholder="https://..."
            />

            <label for="salary">Salary <span class="optional-label">(optional)</span></label>
            <input
              id="salary"
              v-model="salary"
              type="number"
              min="0"
              step="1"
              placeholder="e.g. 30000"
            />

            <label for="notes">Notes <span class="optional-label">(optional)</span></label>
            <textarea
              id="notes"
              v-model="notes"
              rows="3"
              maxlength="2000"
              placeholder="Skills required, interview details, or reminders..."
            ></textarea>

            <p v-if="errorMessage" class="error-message">
              {{ errorMessage }}
            </p>

           
           <button type="submit" :disabled="isSavingApplication">
             {{
              isSavingApplication
              ? 'Saving...'
              : editingId !== null
                ? 'Update application'
                : '+ Add application'
             }}
           </button>

          </form>
        </article>
      </section>

      <footer>CareerTrack · Job Application Tracker</footer>

    </main>
    
<div
  v-if="applicationToDelete"
  class="modal-overlay"
  @click.self="applicationToDelete = null"
>
  <div class="delete-modal">
    <h2>Delete Application?</h2>

    <p>
      Are you sure you want to delete the application for
      <strong>{{ applicationToDelete.company }}</strong>?
      This action cannot be undone.
    </p>

    <div class="modal-actions">
      <button
        type="button"
        class="cancel-button"
        @click="applicationToDelete = null"
      >
        Cancel
      </button>

      <button
        type="button"
        class="confirm-delete-button"
        :disabled="isDeletingApplication"
        @click="confirmDeleteApplication"
      >
        {{ isDeletingApplication ? 'Deleting...' : 'Yes, Delete' }}
      </button>
    </div>
  </div>
</div>

  </div>
</template>

<style>
* {
  box-sizing: border-box;
}

.edit-button {
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  background-color: #fce7e7;
  color: #b91c1c;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.edit-button:hover {
  background-color: #f8d7d7;
}

html,
body,
#app {
  width: 100%;
  min-height: 100%;
  margin: 0;
}

body {
  min-width: 320px;
  display: block;
  font-family: Inter, 'Segoe UI', Arial, sans-serif;
  color: #202a3b;
  background: #f6f8fc;
}

#app {
  max-width: none;
  padding: 0;
  display: block;
}

button,
input,
select,
textarea {
  font: inherit;
}

.app-layout {
  display: flex;
  width: 100%;
  min-height: 100vh;
  background: #f6f8fc;
}

.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 10;
  width: 235px;
  padding: 28px 18px;
  background: #fff;
  border-right: 1px solid #e8ebf2;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 48px;
  font-size: 19px;
  font-weight: 750;
}



.brand-icon img {
  width: 70px;
  height: 70px;
  object-fit: contain;
  display: block;
}

.nav-label {
  margin: 0 10px 12px;
  color: #929caf;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.2px;
}

.nav-item {
  padding: 13px 12px;
  margin-bottom: 7px;
  border-radius: 9px;
  color: #657086;
  font-size: 14px;
}

.nav-item.active {
  color: #4059d4;
  background: #eef1ff;
  font-weight: 650;
}

.sidebar-bottom {
  position: absolute;
  right: 18px;
  bottom: 25px;
  left: 18px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding-top: 18px;
  border-top: 1px solid #edf0f5;
  font-size: 12px;
}

.avatar {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  color: #4059d4;
  background: #e7edff;
  border-radius: 50%;
  font-weight: 700;
}

.sidebar-bottom p {
  margin: 5px 0 0;
  color: #8791a3;
}

.main-content {
  width: calc(100% - 235px);
  min-width: 0;
  max-width: none;
  margin-left: 235px;
  padding: 0 36px 24px;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  height: 70px;
  color: #7b8496;
  font-size: 12px;
  border-bottom: 1px solid #e8ebf2;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.topbar-label {
  font-size: 10px;
  letter-spacing: 1px;
}

.logout-button,
.login-panel form > button,
.add-panel form > button {
  color: #fff;
  background: #4f65e8;
  border: 0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 650;
}

.logout-button {
  padding: 8px 12px;
  white-space: nowrap;
}

.logout-button:hover,
.login-panel form > button:hover,
.add-panel form > button:hover {
  background: #4055d4;
}

.page-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin: 38px 0 28px;
}

.eyebrow {
  margin: 0 0 10px;
  color: #5268e8;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1.2px;
}

h1 {
  margin: 0;
  font-size: clamp(25px, 3vw, 32px);
  letter-spacing: -0.8px;
}

.subtitle {
  margin: 10px 0 0;
  color: #8791a3;
  font-size: 13px;
  line-height: 1.6;
}

.total-badge {
  padding: 10px 14px;
  color: #465ed7;
  background: #edf0ff;
  border-radius: 20px;
  font-size: 12px;
  white-space: nowrap;
}


.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 24px;
  align-items: stretch;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}


.stat-card,
.panel {
  min-width: 0;
  background: #fff;
  border: 1px solid #e9edf4;
  border-radius: 13px;
}

.stat-card {
  padding: 20px;
}

.stat-card p {
  margin: 0 0 16px;
  color: #778195;
  font-size: 12px;
}

.stat-card strong {
  display: block;
  margin: 0 0 12px;
  font-size: 29px;
  line-height: 1.2;
}

.stat-card span {
  display: block;
  color: #929caf;
  font-size: 11px;
  line-height: 1.5;
}

.content-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(280px, 1fr);
  gap: 20px;
  align-items: start;
}

.panel {
  padding: 23px;
}

.panel-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
  margin-bottom: 20px;
}
.application-filters {
  display: flex;
  align-items: center;
  gap: 10px;
}

.application-filters input {
  width: 220px;
  font-size: 12px;
}

.application-filters select {
  width: 140px;
}

@media (max-width: 650px) {
  .application-filters {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .application-filters input,
  .application-filters select {
    width: 100%;
    max-width: none;
  }
}
h2 {
  margin: 0;
  font-size: 16px;
}

.panel-heading p,
.form-description {
  margin: 7px 0 0;
  color: #8791a3;
  font-size: 13px;
  line-height: 1.6;
}

select,
input,
textarea {
  width: 100%;
  padding: 11px 12px;
  color: #30394a;
  background: #fff;
  border: 1px solid #e0e5ee;
  border-radius: 8px;
  outline: none;
}

select {
  width: auto;
  max-width: 145px;
  font-size: 12px;
}

input:focus,
select:focus,
textarea:focus {
  border-color: #6579ed;
}

.application-item {
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 18px 0;
  border-top: 1px solid #edf0f5;
}

.company-icon {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 41px;
  height: 41px;
  color: #465ed7;
  background: #edf0ff;
  border-radius: 11px;
  font-weight: 700;
}

.job-info {
  flex: 1;
  min-width: 0;
}

.job-info strong,
.job-info span,
.job-info small {
  display: block;
}

.job-info strong {
  overflow-wrap: anywhere;
  font-size: 13px;
}

.job-info span {
  margin-top: 5px;
  color: #707b8e;
  font-size: 12px;
}

.job-info small {
  margin-top: 5px;
  color: #a1a8b6;
  font-size: 10px;
}

.status {
  align-self: flex-start;
  flex-shrink: 0;
  padding: 6px 9px;
  border-radius: 20px;
  font-size: 10px;
  white-space: nowrap;
}

.status.applied {
  color: #976b1b;
  background: #fff5d9;
}

.status.interview {
  color: #4260d2;
  background: #eaf0ff;
}

.status.offer {
  color: #187b50;
  background: #e0f7eb;
}

.status.rejected {
  color: #b44646;
  background: #ffebeb;
}

.application-actions {
  display: flex;
  align-items: flex-end;
  gap: 9px;
  flex-wrap: wrap;
}

.status-label {
  display: flex;
  flex-direction: column;
  gap: 5px;
  color: #778195;
  font-size: 10px;
}

.status-label select {
  width: 125px;
  max-width: none;
  padding: 7px 8px;
  font-size: 11px;
}

.delete-button {
  padding: 8px 10px;
  color: #b44646;
  background: #ffebeb;
  border: 0;
  border-radius: 8px;
  cursor: pointer;
  font-size: 11px;
}

.delete-button:hover {
  background: #fbdada;
}

.delete-button:disabled,
.status-label select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.empty-state {
  padding: 25px 0;
  color: #8791a3;
  font-size: 13px;
}

.add-panel form,
.login-panel form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 22px;
}

.add-panel label,
.login-panel label {
  margin-top: 6px;
  color: #515c70;
  font-size: 12px;
  font-weight: 600;
}

.add-panel input,
.add-panel textarea,
.login-panel input {
  font-size: 12px;
}

.add-panel textarea {
  resize: vertical;
  min-height: 80px;
}

.optional-label {
  color: #9aa3b2;
  font-weight: 400;
}

.job-link {
  display: inline-block;
  margin-top: 6px;
  color: #4059d4;
  font-size: 11px;
  text-decoration: none;
}

.job-link:hover {
  text-decoration: underline;
}

.job-notes {
  overflow-wrap: anywhere;
}

.add-panel form > button,
.login-panel form > button {
  margin-top: 10px;
  padding: 12px;
}

.add-panel form > button:disabled,
.login-panel form > button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error-message {
  margin: 4px 0 0;
  color: #c03939;
  font-size: 12px;
}

.success-message {
  margin: 4px 0 0;
  color: #187b50;
  font-size: 12px;
}

.action-error {
  margin: 0 0 18px;
}

footer {
  margin-top: 30px;
  text-align: center;
  color: #a0a8b5;
  font-size: 11px;
}

.login-page {
  display: grid;
  place-items: center;
  min-height: 100vh;
  padding: 24px;
}

.login-panel {
  width: 100%;
  max-width: 420px;
}

.login-panel .brand {
  margin-bottom: 30px;
}

.login-panel h1 {
  font-size: 28px;
}

.auth-switch-text {
  margin: 20px 0 0;
  color: #8791a3;
  text-align: center;
  font-size: 12px;
}

.auth-switch {
  padding: 0;
  color: #4059d4;
  background: none;
  border: 0;
  cursor: pointer;
  font: inherit;
  font-weight: 700;
}

.auth-switch:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 1100px) {
  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 650px) {
  .sidebar {
    position: static;
    width: 100%;
    padding: 16px 20px;
    border-right: 0;
    border-bottom: 1px solid #e8ebf2;
  }

  .brand {
    margin-bottom: 0;
  }

  .nav-label,
  .nav-item,
  .sidebar-bottom {
    display: none;
  }

  .app-layout {
    display: block;
  }

  .main-content {
    width: 100%;
    margin-left: 0;
    padding: 0 16px 20px;
  }

  .page-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .stats-grid {
    gap: 10px;
  }

  .stat-card,
  .panel {
    padding: 15px;
  }

  .stat-card strong {
    font-size: 24px;
  }

  .panel-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  select {
    width: 100%;
    max-width: none;
  }

  .application-item {
    flex-wrap: wrap;
  }

  .application-actions {
    width: 100%;
  }

  .topbar-actions {
    gap: 8px;
  }

  .topbar-label {
    display: none;
  }
}

.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(15, 23, 42, 0.55);
}

.delete-modal {
  width: 100%;
  max-width: 420px;
  padding: 24px;
  border-radius: 16px;
  background: #ffffff;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.delete-modal h2 {
  margin: 0 0 12px;
  color: #1e293b;
  font-size: 20px;
}

.delete-modal p {
  margin: 0 0 24px;
  color: #64748b;
  font-size: 14px;
  line-height: 1.6;
}

.delete-modal strong {
  color: #334155;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.cancel-button,
.confirm-delete-button {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.cancel-button {
  background: #f1f5f9;
  color: #334155;
}

.cancel-button:hover {
  background: #e2e8f0;
}

.confirm-delete-button {
  background: #fee2e2;
  color: #b91c1c;
}

.confirm-delete-button:hover {
  background: #fecaca;
}

.cancel-button:disabled,
.confirm-delete-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.session-loading {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  color: #64748b;
  font-size: 14px;
}
</style>
