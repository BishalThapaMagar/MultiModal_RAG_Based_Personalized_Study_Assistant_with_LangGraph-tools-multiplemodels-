import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { useToast } from '@/hooks/use-toast';
import { useQuiz } from '@/contexts/QuizContext';
import { processFile } from '@/services/api';
import heroImage from '@/assets/hero-image.jpg';

const UploadPage: React.FC = () => {
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { setProcessedData } = useQuiz();
  const { toast } = useToast();
  const navigate = useNavigate();

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      const file = files[0];
      if (file.type === 'application/pdf') {
        setSelectedFile(file);
      } else {
        toast({
          title: "Invalid file type",
          description: "Please select a PDF file.",
          variant: "destructive"
        });
      }
    }
  }, [toast]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
    } else if (file) {
      toast({
        title: "Invalid file type",
        description: "Please select a PDF file.",
        variant: "destructive"
      });
    }
  }, [toast]);

  const handleSubmit = async () => {
    if (!selectedFile) return;

    setLoading(true);
    try {
      const result = await processFile(selectedFile);
      setProcessedData(result);
      
      toast({
        title: "PDF processed successfully!",
        description: `Generated summary and ${result.quiz.length} quiz questions.`,
      });
      
      navigate('/summary');
    } catch (error) {
      console.error('Error processing file:', error);
      toast({
        title: "Processing failed",
        description: "Failed to process your PDF. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-secondary">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative overflow-hidden"
      >
        <div className="absolute inset-0">
          <img
            src={heroImage}
            alt="Learning Platform"
            className="w-full h-full object-cover opacity-80"
          />
          <div className="absolute inset-0 gradient-primary opacity-90" />
        </div>
        
        <div className="relative z-10 container mx-auto px-4 py-20 text-center text-white">
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="text-5xl md:text-6xl font-bold mb-6"
          >
            PDF Quest Genius
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.6 }}
            className="text-xl md:text-2xl opacity-90 max-w-2xl mx-auto"
          >
            Transform any PDF into an engaging learning experience with AI-powered summaries and interactive quizzes
          </motion.p>
        </div>
      </motion.div>

      {/* Upload Section */}
      <div className="container mx-auto px-4 py-16 -mt-10 relative z-20">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.6 }}
          className="max-w-2xl mx-auto"
        >
          <Card className="p-8 shadow-strong border-0 bg-card/95 backdrop-blur-sm">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-foreground mb-2">
                Upload Your PDF
              </h2>
              <p className="text-muted-foreground">
                Choose a PDF file to generate an interactive summary and quiz
              </p>
            </div>

            <div
              className={`
                relative border-2 border-dashed rounded-xl p-12 text-center transition-smooth cursor-pointer
                ${dragActive 
                  ? 'border-primary bg-primary/5 scale-105' 
                  : selectedFile 
                    ? 'border-success bg-success/5' 
                    : 'border-border hover:border-primary/50 hover:bg-primary/5'
                }
              `}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => document.getElementById('file-input')?.click()}
            >
              <input
                id="file-input"
                type="file"
                accept=".pdf"
                onChange={handleFileSelect}
                className="hidden"
              />
              
              <motion.div
                animate={dragActive ? { scale: 1.1 } : { scale: 1 }}
                transition={{ duration: 0.2 }}
                className="flex flex-col items-center"
              >
                {selectedFile ? (
                  <>
                    <FileText className="w-16 h-16 text-success mb-4" />
                    <h3 className="text-xl font-semibold text-success mb-2">
                      File Selected
                    </h3>
                    <p className="text-muted-foreground mb-4">
                      {selectedFile.name}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Click to change file or drag a new one here
                    </p>
                  </>
                ) : (
                  <>
                    <Upload className="w-16 h-16 text-primary mb-4" />
                    <h3 className="text-xl font-semibold text-foreground mb-2">
                      Drop your PDF here
                    </h3>
                    <p className="text-muted-foreground mb-4">
                      or click to browse files
                    </p>
                    <p className="text-sm text-muted-foreground">
                      Supports PDF files up to 10MB
                    </p>
                  </>
                )}
              </motion.div>
            </div>

            {selectedFile && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-8 flex justify-center"
              >
                <Button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="gradient-primary text-white px-8 py-3 text-lg font-semibold shadow-medium hover:shadow-strong transition-smooth"
                >
                  {loading ? (
                    <div className="flex items-center">
                      <LoadingSpinner size="sm" className="mr-2" />
                      Processing PDF...
                    </div>
                  ) : (
                    'Generate Summary & Quiz'
                  )}
                </Button>
              </motion.div>
            )}
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default UploadPage;