import React, { createContext, useContext, useState, ReactNode } from 'react';

interface QuizQuestion {
  question: string;
  options: string[];
  answer: string;
}

interface ProcessedData {
  filename: string;
  summary: string;
  quiz: QuizQuestion[];
}

interface QuizContextType {
  processedData: ProcessedData | null;
  setProcessedData: (data: ProcessedData) => void;
  currentQuizIndex: number;
  setCurrentQuizIndex: (index: number) => void;
  userAnswers: string[];
  setUserAnswer: (index: number, answer: string) => void;
  quizScore: number | null;
  setQuizScore: (score: number) => void;
  resetQuiz: () => void;
}

const QuizContext = createContext<QuizContextType | undefined>(undefined);

export const useQuiz = () => {
  const context = useContext(QuizContext);
  if (!context) {
    throw new Error('useQuiz must be used within a QuizProvider');
  }
  return context;
};

interface QuizProviderProps {
  children: ReactNode;
}

export const QuizProvider: React.FC<QuizProviderProps> = ({ children }) => {
  const [processedData, setProcessedData] = useState<ProcessedData | null>(null);
  const [currentQuizIndex, setCurrentQuizIndex] = useState(0);
  const [userAnswers, setUserAnswersState] = useState<string[]>([]);
  const [quizScore, setQuizScore] = useState<number | null>(null);

  const setUserAnswer = (index: number, answer: string) => {
    setUserAnswersState(prev => {
      const newAnswers = [...prev];
      newAnswers[index] = answer;
      return newAnswers;
    });
  };

  const resetQuiz = () => {
    setCurrentQuizIndex(0);
    setUserAnswersState([]);
    setQuizScore(null);
  };

  return (
    <QuizContext.Provider
      value={{
        processedData,
        setProcessedData,
        currentQuizIndex,
        setCurrentQuizIndex,
        userAnswers,
        setUserAnswer,
        quizScore,
        setQuizScore,
        resetQuiz,
      }}
    >
      {children}
    </QuizContext.Provider>
  );
};