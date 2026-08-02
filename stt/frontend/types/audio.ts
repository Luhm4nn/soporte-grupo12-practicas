export interface Segment {
  start: number
  end: number
  text: string
}

export interface AudioUploadResponse {
  id: string
  original_name: string
  file_size: number
  status: string
  message: string
}

export interface AudioData {
  id: string
  original_name: string
  duration: number | null
  language: string | null
  status: string
  error_message: string | null
  created_at: string
  updated_at: string
  transcription_text: string | null
  transcription_segments: Segment[] | null
  tags: string[] | null
  tasks: Task[] | null
  dates: string[] | null
  emails: string[] | null
  phones: string[] | null
  links: string[] | null
  summary_short: string | null
  summary_medium: string | null
  summary_detailed: string | null
  improved_text: string | null
  text_no_fillers: string | null
}

export interface Task {
  task: string
  deadline: string | null
  responsible: string | null
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}
