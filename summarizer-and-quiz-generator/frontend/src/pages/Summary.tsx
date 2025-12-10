import React from 'react';
import { motion } from 'framer-motion';
import { FileText, Clock, BookOpen, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useQuiz } from '@/contexts/QuizContext';

const SummaryPage: React.FC = () => {
  const { processedData, resetQuiz } = useQuiz();
  const navigate = useNavigate();

  if (!processedData) {
    navigate('/');
    return null;
  }

  const handleTakeQuiz = () => {
    resetQuiz();
    navigate('/quiz');
  };

  const estimatedReadTime = Math.ceil(processedData.summary.split(' ').length / 200);

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
          <div className="text-center mb-12">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="inline-flex items-center mb-4 px-4 py-2 bg-primary/10 rounded-full"
            >
              <FileText className="w-5 h-5 text-primary mr-2" />
              <span className="text-primary font-medium">Document Processed</span>
            </motion.div>
            
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.6 }}
              className="text-4xl md:text-5xl font-bold text-foreground mb-4"
            >
              {processedData.filename}
            </motion.h1>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.6 }}
              className="flex items-center justify-center gap-6 text-muted-foreground"
            >
              <div className="flex items-center">
                <Clock className="w-4 h-4 mr-1" />
                <span>{estimatedReadTime} min read</span>
              </div>
              <div className="flex items-center">
                <BookOpen className="w-4 h-4 mr-1" />
                <span>{processedData.quiz.length} quiz questions</span>
              </div>
            </motion.div>
          </div>

          {/* Summary Card */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
            className="mb-8"
          >
            <Card className="shadow-medium border-0 bg-card/95 backdrop-blur-sm">
              <CardHeader className="pb-6">
                <CardTitle className="flex items-center text-2xl font-bold text-foreground">
                  <FileText className="w-6 h-6 text-primary mr-3" />
                  Summary
                  <Badge variant="secondary" className="ml-auto">
                    AI Generated
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="prose prose-lg max-w-none">
                  <div className="text-foreground leading-relaxed whitespace-pre-wrap font-medium">
                    {processedData.summary}
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Quiz Preview */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7, duration: 0.6 }}
            className="mb-8"
          >
            <Card className="shadow-medium border-0 bg-card/95 backdrop-blur-sm overflow-hidden">
              <CardHeader className="gradient-primary text-white">
                <CardTitle className="flex items-center text-2xl font-bold">
                  <BookOpen className="w-6 h-6 mr-3" />
                  Interactive Quiz Ready
                </CardTitle>
                <p className="text-white/90 mt-2">
                  Test your understanding with {processedData.quiz.length} carefully crafted questions
                </p>
              </CardHeader>
              <CardContent className="p-8">
                <div className="grid md:grid-cols-3 gap-6 mb-8">
                  <div className="text-center">
                    <div className="w-12 h-12 gradient-primary rounded-full flex items-center justify-center mx-auto mb-3">
                      <span className="text-white font-bold text-xl">
                        {processedData.quiz.length}
                      </span>
                    </div>
                    <h3 className="font-semibold text-foreground">Questions</h3>
                    <p className="text-muted-foreground text-sm">
                      Multiple choice format
                    </p>
                  </div>
                  
                  <div className="text-center">
                    <div className="w-12 h-12 bg-success/20 rounded-full flex items-center justify-center mx-auto mb-3">
                      <span className="text-success font-bold text-xl">✓</span>
                    </div>
                    <h3 className="font-semibold text-foreground">Instant Feedback</h3>
                    <p className="text-muted-foreground text-sm">
                      See results immediately
                    </p>
                  </div>
                  
                  <div className="text-center">
                    <div className="w-12 h-12 bg-accent/20 rounded-full flex items-center justify-center mx-auto mb-3">
                      <span className="text-accent-foreground font-bold text-xl">📊</span>
                    </div>
                    <h3 className="font-semibold text-foreground">Score Tracking</h3>
                    <p className="text-muted-foreground text-sm">
                      Performance analytics
                    </p>
                  </div>
                </div>

                <div className="text-center">
                  <Button
                    onClick={handleTakeQuiz}
                    className="gradient-primary text-white px-8 py-4 text-lg font-semibold shadow-medium hover:shadow-strong transition-spring group"
                  >
                    Take Quiz Now
                    <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-smooth" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Back to Upload */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.9, duration: 0.6 }}
            className="text-center"
          >
            <Button
              onClick={() => navigate('/')}
              variant="outline"
              className="text-muted-foreground hover:text-foreground"
            >
              Upload Another PDF
            </Button>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
};

export default SummaryPage;