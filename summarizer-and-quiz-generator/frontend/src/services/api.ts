import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export interface ProcessResponse {
  filename: string;
  summary: string;
  quiz: Array<{
    question: string;
    options: string[];
    answer: string;
  }>;
}

export const processFile = async (file: File): Promise<ProcessResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await axios.post<ProcessResponse>(
    `${API_BASE_URL}/process`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );

  return response.data;
};