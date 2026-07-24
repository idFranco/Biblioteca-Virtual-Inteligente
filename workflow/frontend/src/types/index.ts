export interface User {
  id: string
  fullName: string
  email: string
  roles: string[]
  permissions: string[]
}

export interface AuthTokens {
  accessToken: string
  refreshToken: string
}
