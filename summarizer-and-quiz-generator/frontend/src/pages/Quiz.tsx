import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, RotateCcw, Trophy, Target } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { useQuiz } from '@/contexts/QuizContext';

const QuizPage: React.FC = () => {
  const { processedData, userAnswers, setUserAnswer, quizScore, setQuizScore } = useQuiz();
  const [showResults, setShowResults] = useState(false);
  const [currentAnswer, setCurrentAnswer] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    if (!processedData) {
      navigate('/');
    }
  }, [processedData, navigate]);

  if (!processedData) return null;

  const handleAnswerSelect = (questionIndex: number, answer: string) => {
    setUserAnswer(questionIndex, answer);
    setCurrentAnswer(answer);
  };

  const calculateScore = () => {
    let correct = 0;
    processedData.quiz.forEach((question, index) => {
      if (userAnswers[index] === question.answer) {
        correct++;
      }
    });
    return correct;
  };

  const handleSubmitQuiz = () => {
    const score = calculateScore();
    setQuizScore(score);
    setShowResults(true);
  };

  const canSubmit = userAnswers.length === processedData.quiz.length && 
                   userAnswers.every(answer => answer !== undefined && answer !== '');

  const scorePercentage = quizScore !== null ? Math.round((quizScore / processedData.quiz.length) * 100) : 0;
  
  const getScoreMessage = () => {
    if (scorePercentage >= 90) return { text: "Outstanding! 🏆", color: "text-yellow-600" };
    if (scorePercentage >= 80) return { text: "Excellent! 🌟", color: "text-success" };
    if (scorePercentage >= 70) return { text: "Great job! 👏", color: "text-success" };
    if (scorePercentage >= 60) return { text: "Good effort! 👍", color: "text-primary" };
    return { text: "Keep practicing! 💪", color: "text-muted-foreground" };
  };

  if (showResults && quizScore !== null) {
    const scoreMessage = getScoreMessage();
    
    return (
      <div className="min-h-screen bg-gradient-secondary">
        <div className="container mx-auto px-4 py-12">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="max-w-4xl mx-auto"
          >
            {/* Score Overview */}
            <Card className="mb-8 shadow-strong border-0 bg-card/95 backdrop-blur-sm overflow-hidden">
              <CardHeader className="gradient-primary text-white text-center py-12">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.3, type: "spring" }}
                  className="flex items-center justify-center mb-4"
                >
                  <Trophy className="w-16 h-16" />
                </motion.div>
                <CardTitle className="text-4xl font-bold mb-2">Quiz Complete!</CardTitle>
                <p className="text-white/90 text-xl">
                  You scored {quizScore} out of {processedData.quiz.length} questions
                </p>
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.5, type: "spring" }}
                  className="mt-6"
                >
                  <div className={`text-6xl font-bold ${scoreMessage.color.replace('text-', 'text-white')}`}>
                    {scorePercentage}%
                  </div>
                  <div className={`text-2xl mt-2 ${scoreMessage.color.replace('text-', 'text-white/90')}`}>
                    {scoreMessage.text}
                  </div>
                </motion.div>
              </CardHeader>
            </Card>

            {/* Question Results */}
            <div className="space-y-6 mb-8">
              {processedData.quiz.map((question, index) => {
                const userAnswer = userAnswers[index];
                const isCorrect = userAnswer === question.answer;
                
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                  >
                    <Card className="shadow-medium border-0 bg-card/95 backdrop-blur-sm">
                      <CardHeader className="pb-4">
                        <div className="flex items-start justify-between">
                          <CardTitle className="text-lg font-semibold text-foreground">
                            Question {index + 1}
                          </CardTitle>
                          <Badge variant={isCorrect ? "default" : "destructive"} className="shrink-0">
                            {isCorrect ? (
                              <><CheckCircle className="w-4 h-4 mr-1" /> Correct</>
                            ) : (
                              <><XCircle className="w-4 h-4 mr-1" /> Incorrect</>
                            )}
                          </Badge>
                        </div>
                        <p className="text-foreground font-medium">{question.question}</p>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {question.options.map((option, optionIndex) => {
                            const isUserAnswer = option === userAnswer;
                            const isCorrectAnswer = option === question.answer;
                            
                            let optionClass = "p-4 rounded-lg border transition-smooth";
                            if (isCorrectAnswer) {
                              optionClass += " bg-success/10 border-success text-success-foreground font-semibold";
                            } else if (isUserAnswer && !isCorrect) {
                              optionClass += " bg-destructive/10 border-destructive text-destructive-foreground";
                            } else {
                              optionClass += " bg-muted/50 border-border text-muted-foreground";
                            }
                            
                            return (
                              <div key={optionIndex} className={optionClass}>
                                <div className="flex items-center">
                                  {isCorrectAnswer && (
                                    <CheckCircle className="w-5 h-5 mr-3 text-success" />
                                  )}
                                  {isUserAnswer && !isCorrect && (
                                    <XCircle className="w-5 h-5 mr-3 text-destructive" />
                                  )}
                                  <span>{option}</span>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                onClick={() => navigate('/summary')}
                variant="outline"
                className="text-muted-foreground hover:text-foreground"
              >
                Back to Summary
              </Button>
              <Button
                onClick={() => navigate('/')}
                className="gradient-primary text-white shadow-medium hover:shadow-strong transition-smooth"
              >
                Upload Another PDF
              </Button>
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-secondary">
      <div className="container mx-auto px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-4xl mx-auto"
        >
          {/* Header */}
          <div className="text-center mb-8">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="inline-flex items-center mb-4 px-4 py-2 bg-primary/10 rounded-full"
            >
              <Target className="w-5 h-5 text-primary mr-2" />
              <span className="text-primary font-medium">Interactive Quiz</span>
            </motion.div>
            
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.6 }}
              className="text-4xl md:text-5xl font-bold text-foreground mb-4"
            >
              Test Your Knowledge
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.6 }}
              className="text-muted-foreground text-lg"
            >
              Answer all questions to see your results
            </motion.p>
          </div>

          {/* Progress */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            className="mb-8"
          >
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-foreground">Progress</span>
              <span className="text-sm text-muted-foreground">
                {userAnswers.filter(a => a).length} / {processedData.quiz.length}
              </span>
            </div>
            <Progress 
              value={(userAnswers.filter(a => a).length / processedData.quiz.length) * 100} 
              className="h-2"
            />
          </motion.div>

          {/* Questions */}
          <div className="space-y-8 mb-8">
            <AnimatePresence>
              {processedData.quiz.map((question, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 40 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 + index * 0.1, duration: 0.6 }}
                >
                  <Card className="shadow-medium border-0 bg-card/95 backdrop-blur-sm">
                    <CardHeader>
                      <CardTitle className="flex items-center text-xl font-bold text-foreground">
                        <span className="w-8 h-8 gradient-primary rounded-full flex items-center justify-center text-white font-bold mr-4 text-sm">
                          {index + 1}
                        </span>
                        {question.question}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <RadioGroup
                        value={userAnswers[index] || ''}
                        onValueChange={(value) => handleAnswerSelect(index, value)}
                      >
                        <div className="space-y-4">
                          {question.options.map((option, optionIndex) => (
                            <motion.div
                              key={optionIndex}
                              whileHover={{ scale: 1.01 }}
                              whileTap={{ scale: 0.99 }}
                            >
                              <div className="flex items-center space-x-3 p-4 rounded-lg border border-border hover:border-primary/50 hover:bg-primary/5 transition-smooth cursor-pointer">
                                <RadioGroupItem
                                  value={option}
                                  id={`q${index}-option${optionIndex}`}
                                  className="shrink-0"
                                />
                                <Label
                                  htmlFor={`q${index}-option${optionIndex}`}
                                  className="flex-1 cursor-pointer font-medium text-foreground"
                                >
                                  {option}
                                </Label>
                              </div>
                            </motion.div>
                          ))}
                        </div>
                      </RadioGroup>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {/* Submit Button */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1, duration: 0.6 }}
            className="text-center"
          >
            <Button
              onClick={handleSubmitQuiz}
              disabled={!canSubmit}
              className="gradient-primary text-white px-8 py-4 text-lg font-semibold shadow-medium hover:shadow-strong transition-spring disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {canSubmit ? 'Submit Quiz' : `Answer ${processedData.quiz.length - userAnswers.filter(a => a).length} more question${processedData.quiz.length - userAnswers.filter(a => a).length !== 1 ? 's' : ''}`}
            </Button>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
};

export default QuizPage;