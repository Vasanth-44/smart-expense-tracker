import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, X, FileText, CheckCircle, AlertCircle, Download } from 'lucide-react';
import axios from 'axios';
import Modal from './ui/Modal';
import Button from './ui/Button';
import GlassCard from './ui/GlassCard';
import toast from 'react-hot-toast';
import { API_BASE_URL } from '../services/api';

export default function CSVImport({ isOpen, onClose, onSuccess }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (selectedFile) => {
    if (!selectedFile.name.endsWith('.csv')) {
      toast.error('Please upload a CSV file');
      return;
    }

    setFile(selectedFile);
    setResult(null);
    setUploading(true);

    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', selectedFile);

      const res = await axios.post(
        `${API_BASE_URL}/expenses/validate-csv`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      if (res.data.valid) {
        setPreview(res.data);
        toast.success(`Found ${res.data.total_rows} valid rows`);
      } else {
        toast.error('Invalid CSV format');
        setPreview(res.data);
      }
    } catch (error) {
      console.error('Error validating CSV:', error);
      toast.error('Failed to validate CSV file');
    } finally {
      setUploading(false);
    }
  };

  const handleImport = async () => {
    if (!file) return;

    setImporting(true);
    try {
      const token = localStorage.getItem('token');
      const formData = new FormData();
      formData.append('file', file);

      const res = await axios.post(
        `${API_BASE_URL}/expenses/import-csv`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      setResult(res.data);
      toast.success(`Imported ${res.data.imported} expenses!`);
      
      if (res.data.imported > 0) {
        setTimeout(() => {
          onSuccess();
          handleClose();
        }, 3000);
      }
    } catch (error) {
      console.error('Error importing CSV:', error);
      toast.error('Failed to import expenses');
    } finally {
      setImporting(false);
    }
  };

  const handleClose = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
    onClose();
  };

  const downloadSample = () => {
    const sample = `date,description,amount
2024-02-10,Swiggy food order,450
2024-02-09,Uber ride to office,200
2024-02-08,Amazon shopping,1500
2024-02-07,Gym membership,800`;
    
    const blob = new Blob([sample], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_expenses.csv';
    a.click();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Import Expenses from CSV">
      <div className="space-y-6">
        {/* Instructions */}
        {!file && !result && (
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
            <h4 className="text-blue-300 font-medium mb-2">CSV Format</h4>
            <p className="text-sm text-gray-300 mb-3">
              Your CSV should have columns: <code className="text-blue-300">date</code>, <code className="text-blue-300">description</code>, <code className="text-blue-300">amount</code>
            </p>
            <button
              onClick={downloadSample}
              className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
            >
              <Download size={14} />
              Download sample CSV
            </button>
          </div>
        )}

        {/* Upload Area */}
        {!file && !result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`
              border-2 border-dashed rounded-2xl p-12 text-center transition-all
              ${dragActive 
                ? 'border-indigo-500 bg-indigo-500/10' 
                : 'border-white/20 hover:border-white/40'
              }
            `}
          >
            <Upload size={48} className="mx-auto mb-4 text-gray-400" />
            <p className="text-white mb-2">Drag and drop your CSV file here</p>
            <p className="text-gray-400 text-sm mb-4">or</p>
            <label className="cursor-pointer">
              <span className="px-4 py-2 bg-indigo-500 hover:bg-indigo-600 text-white rounded-xl inline-block transition">
                Browse Files
              </span>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileInput}
                className="hidden"
              />
            </label>
          </motion.div>
        )}

        {/* Preview */}
        {preview && !result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="text-indigo-400" size={20} />
                <span className="text-white font-medium">{file.name}</span>
              </div>
              <button
                onClick={() => {
                  setFile(null);
                  setPreview(null);
                }}
                className="text-gray-400 hover:text-white"
              >
                <X size={20} />
              </button>
            </div>

            {preview.valid ? (
              <>
                <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-4">
                  <div className="flex items-center gap-2 text-green-300 mb-2">
                    <CheckCircle size={20} />
                    <span className="font-medium">Valid CSV</span>
                  </div>
                  <p className="text-sm text-gray-300">
                    Found {preview.total_rows} expenses ready to import
                  </p>
                </div>

                {/* Preview Table */}
                <div className="bg-white/5 rounded-xl overflow-hidden">
                  <div className="p-3 border-b border-white/10">
                    <h4 className="text-white font-medium">Preview (first 5 rows)</h4>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead className="bg-white/5">
                        <tr>
                          <th className="px-4 py-2 text-left text-gray-400">Date</th>
                          <th className="px-4 py-2 text-left text-gray-400">Description</th>
                          <th className="px-4 py-2 text-left text-gray-400">Category</th>
                          <th className="px-4 py-2 text-right text-gray-400">Amount</th>
                        </tr>
                      </thead>
                      <tbody>
                        {preview.preview.map((row, idx) => (
                          <tr key={idx} className="border-t border-white/5">
                            <td className="px-4 py-2 text-gray-300">{row.date}</td>
                            <td className="px-4 py-2 text-gray-300">{row.note}</td>
                            <td className="px-4 py-2">
                              <span className="px-2 py-1 bg-indigo-500/20 text-indigo-300 rounded text-xs">
                                {row.category}
                              </span>
                            </td>
                            <td className="px-4 py-2 text-right text-white">₹{row.amount}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                <Button
                  onClick={handleImport}
                  loading={importing}
                  className="w-full"
                >
                  Import {preview.total_rows} Expenses
                </Button>
              </>
            ) : (
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                <div className="flex items-center gap-2 text-red-300 mb-2">
                  <AlertCircle size={20} />
                  <span className="font-medium">Invalid CSV</span>
                </div>
                <p className="text-sm text-gray-300 mb-2">
                  {preview.error || 'Unable to parse CSV file'}
                </p>
                {preview.errors && preview.errors.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {preview.errors.slice(0, 5).map((error, idx) => (
                      <p key={idx} className="text-xs text-red-300">• {error}</p>
                    ))}
                  </div>
                )}
              </div>
            )}
          </motion.div>
        )}

        {/* Result Summary */}
        {result && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="space-y-4"
          >
            <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-6 text-center">
              <CheckCircle size={48} className="mx-auto mb-4 text-green-400" />
              <h3 className="text-2xl font-bold text-white mb-2">
                Import Complete!
              </h3>
              <p className="text-gray-300">
                Successfully imported {result.imported} out of {result.total_rows} expenses
              </p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-white/5 rounded-xl p-4 text-center">
                <p className="text-2xl font-bold text-green-400">{result.imported}</p>
                <p className="text-xs text-gray-400">Imported</p>
              </div>
              <div className="bg-white/5 rounded-xl p-4 text-center">
                <p className="text-2xl font-bold text-yellow-400">{result.duplicates}</p>
                <p className="text-xs text-gray-400">Duplicates</p>
              </div>
              <div className="bg-white/5 rounded-xl p-4 text-center">
                <p className="text-2xl font-bold text-red-400">{result.failed}</p>
                <p className="text-xs text-gray-400">Failed</p>
              </div>
            </div>

            {/* Category Summary */}
            {result.category_summary && Object.keys(result.category_summary).length > 0 && (
              <div className="bg-white/5 rounded-xl p-4">
                <h4 className="text-white font-medium mb-3">Categories Detected</h4>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(result.category_summary).map(([category, count]) => (
                    <span
                      key={category}
                      className="px-3 py-1 bg-indigo-500/20 text-indigo-300 rounded-full text-sm"
                    >
                      {category}: {count}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <Button onClick={handleClose} className="w-full">
              Done
            </Button>
          </motion.div>
        )}
      </div>
    </Modal>
  );
}
