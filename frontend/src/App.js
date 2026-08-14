import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { HomeIcon, DocumentIcon, MagnifyingGlassIcon, QuestionMarkCircleIcon, ChartBarIcon } from '@heroicons/react/24/outline';
import { uploadDocument, searchDocuments, askQuestion, deleteDocument, getDocumentDetails, evaluateRetrieval, evaluateGeneration } from './services/api';
import api from './services/api';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Navigation */}
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <div className="flex-shrink-0 flex items-center">
                  <h1 className="text-xl font-bold text-primary-600">Document Processing</h1>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  <Link
                    to="/"
                    className="border-transparent text-gray-500 hover:border-primary-500 hover:text-primary-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    <HomeIcon className="h-5 w-5 mr-1" />
                    Home
                  </Link>
                  <Link
                    to="/documents"
                    className="border-transparent text-gray-500 hover:border-primary-500 hover:text-primary-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    <DocumentIcon className="h-5 w-5 mr-1" />
                    Documents
                  </Link>
                  <Link
                    to="/search"
                    className="border-transparent text-gray-500 hover:border-primary-500 hover:text-primary-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    <MagnifyingGlassIcon className="h-5 w-5 mr-1" />
                    Search
                  </Link>
                  <Link
                    to="/qa"
                    className="border-transparent text-gray-500 hover:border-primary-500 hover:text-primary-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    <QuestionMarkCircleIcon className="h-5 w-5 mr-1" />
                    Q&A
                  </Link>
                  <Link
                    to="/evaluate"
                    className="border-transparent text-gray-500 hover:border-primary-500 hover:text-primary-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
                  >
                    <ChartBarIcon className="h-5 w-5 mr-1" />
                    Evaluate
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="border-4 border-dashed border-gray-200 rounded-lg p-6">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/documents" element={<Documents />} />
                <Route path="/search" element={<Search />} />
                <Route path="/qa" element={<QA />} />
                <Route path="/evaluate" element={<Evaluate />} />
              </Routes>
            </div>
          </div>
        </main>
      </div>
    </Router>
  );
}

function Home() {
  const [recentDocuments, setRecentDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchRecentDocuments();
  }, []);

  const fetchRecentDocuments = async () => {
    try {
      const response = await api.get('/documents');
      // Sort by created_at and take the 5 most recent
      const sorted = response.data.sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
      );
      setRecentDocuments(sorted.slice(0, 5));
    } catch (err) {
      setError('Failed to fetch recent documents');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setSearching(true);
    try {
      const results = await searchDocuments(searchQuery);
      setSearchResults(results);
    } catch (err) {
      setError('Search failed');
    } finally {
      setSearching(false);
    }
  };

  const handleQuickUpload = async () => {
    if (!file) return;

    setUploading(true);
    try {
      await uploadDocument(file);
      setFile(null);
      fetchRecentDocuments(); // Refresh the recent documents list
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <div className="text-center mb-12">
      <h2 className="text-3xl font-bold text-gray-900 mb-4">Welcome to Document Processing</h2>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Upload, search, and analyze your documents with ease. Get started by uploading a document or searching through your existing ones.
        </p>
      </div>

      {/* Quick Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        {/* Quick Upload */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Upload</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
              <div className="space-y-1 text-center">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  stroke="currentColor"
                  fill="none"
                  viewBox="0 0 48 48"
                  aria-hidden="true"
                >
                  <path
                    d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                    strokeWidth={2}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                <div className="flex text-sm text-gray-600">
                  <label
                    htmlFor="quick-upload"
                    className="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500"
                  >
                    <span>Upload a file</span>
                    <input
                      id="quick-upload"
                      name="quick-upload"
                      type="file"
                      className="sr-only"
                      onChange={(e) => setFile(e.target.files[0])}
                      accept=".pdf,.jpg,.jpeg,.png,.txt"
                    />
                  </label>
                </div>
              </div>
            </div>
            {file && (
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-600">{file.name}</p>
                <button
                  onClick={handleQuickUpload}
                  disabled={uploading}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  {uploading ? 'Uploading...' : 'Upload'}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Quick Search */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Search</h3>
          <div className="space-y-4">
            <div className="flex rounded-md shadow-sm">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleQuickSearch()}
                className="focus:ring-primary-500 focus:border-primary-500 flex-1 block w-full rounded-md sm:text-sm border-gray-300"
                placeholder="Search your documents..."
              />
              <button
                onClick={handleQuickSearch}
                disabled={searching}
                className="ml-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                {searching ? 'Searching...' : 'Search'}
              </button>
            </div>
            {searchResults.length > 0 && (
              <div className="mt-4 space-y-2">
                {searchResults.slice(0, 3).map((result, index) => (
                  <div key={index} className="text-sm text-gray-600 p-2 bg-gray-50 rounded">
                    {result.text}
                  </div>
                ))}
                {searchResults.length > 3 && (
                  <Link
                    to="/search"
                    className="text-sm text-primary-600 hover:text-primary-500"
                  >
                    View all results →
                  </Link>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Documents */}
      <div className="bg-white rounded-lg shadow p-6 mb-12">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">Recent Documents</h3>
          <Link
            to="/documents"
            className="text-sm text-primary-600 hover:text-primary-500"
          >
            View all →
          </Link>
        </div>
        {loading ? (
          <p className="text-sm text-gray-600">Loading recent documents...</p>
        ) : error ? (
          <p className="text-sm text-red-600">{error}</p>
        ) : recentDocuments.length === 0 ? (
          <p className="text-sm text-gray-600">No documents uploaded yet</p>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {recentDocuments.map((doc) => (
              <div key={doc.id} className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate" title={doc.filename}>
                      {doc.filename}
                    </p>
                    <p className="text-xs text-gray-500">
                      Uploaded: {new Date(doc.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <Link
                    to={`/documents`}
                    className="ml-4 text-primary-600 hover:text-primary-700"
                  >
                    View
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Feature Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white mb-4">
            <DocumentIcon className="h-6 w-6" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Document Management</h3>
          <p className="text-sm text-gray-600">
            Upload and organize your documents with ease. Support for PDF, images, and text files.
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white mb-4">
            <MagnifyingGlassIcon className="h-6 w-6" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Smart Search</h3>
          <p className="text-sm text-gray-600">
            Search through your documents using natural language queries and find exactly what you need.
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white mb-4">
            <QuestionMarkCircleIcon className="h-6 w-6" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Q&A System</h3>
          <p className="text-sm text-gray-600">
            Ask questions about your documents and get instant answers powered by AI.
          </p>
        </div>
      </div>
    </div>
  );
}

function Documents() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [loadingContent, setLoadingContent] = useState(false);

  const fetchDocuments = async () => {
    try {
      const response = await api.get('/documents');
      setDocuments(response.data);
    } catch (err) {
      setError('Failed to fetch documents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      await uploadDocument(file);
      setFile(null);
      fetchDocuments(); // Refresh the document list
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    setDeleting(true);
    try {
      await deleteDocument(documentId);
      fetchDocuments(); // Refresh the document list
    } catch (err) {
      setError(err.message);
    } finally {
      setDeleting(false);
    }
  };

  const handleViewDocument = async (doc) => {
    setSelectedDocument(doc);
    setLoadingContent(true);
    try {
      const documentDetails = await getDocumentDetails(doc.id);
      setSelectedDocument(documentDetails);
    } catch (err) {
      setError('Failed to load document content');
    } finally {
      setLoadingContent(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Documents</h2>
      
      {/* Upload Section */}
      <div className="max-w-xl mx-auto mb-8">
        <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
          <div className="space-y-1 text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
              aria-hidden="true"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div className="flex text-sm text-gray-600">
              <label
                htmlFor="file-upload"
                className="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500"
              >
                <span>Upload a file</span>
                <input
                  id="file-upload"
                  name="file-upload"
                  type="file"
                  className="sr-only"
                  onChange={(e) => setFile(e.target.files[0])}
                  accept=".pdf,.jpg,.jpeg,.png,.txt"
                />
              </label>
              <p className="pl-1">or drag and drop</p>
            </div>
            <p className="text-xs text-gray-500">PDF, JPG, PNG, or TXT up to 10MB</p>
          </div>
        </div>

        {file && (
          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-gray-600">{file.name}</p>
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </div>
        )}

        {error && (
          <div className="mt-4 p-4 bg-red-50 rounded-md">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}
      </div>

      {/* Document List */}
      <div className="mt-8">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Uploaded Documents</h3>
        {loading ? (
          <p className="text-sm text-gray-600">Loading documents...</p>
        ) : documents.length === 0 ? (
          <p className="text-sm text-gray-600">No documents uploaded yet</p>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {documents.map((doc) => (
              <div key={doc.id} className="bg-white shadow rounded-lg p-4">
                <div className="flex flex-col space-y-2">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0 pr-4">
                      <p className="text-sm font-medium text-gray-900 truncate" title={doc.filename}>
                        {doc.filename}
                      </p>
                    <p className="text-xs text-gray-500">
                      Type: {doc.file_type} • Uploaded: {new Date(doc.created_at).toLocaleDateString()}
                    </p>
                  </div>
                    <div className="flex-shrink-0 flex space-x-2">
                    <button
                        onClick={() => handleViewDocument(doc)}
                        className="text-primary-600 hover:text-primary-700 px-2 py-1 rounded hover:bg-gray-50"
                    >
                      View
                    </button>
                    <button
                      onClick={() => handleDelete(doc.id)}
                      disabled={deleting}
                        className="text-red-600 hover:text-red-700 px-2 py-1 rounded hover:bg-gray-50"
                    >
                      {deleting ? 'Deleting...' : 'Delete'}
                    </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Document View Modal */}
      {selectedDocument && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-medium text-gray-900 truncate max-w-2xl" title={selectedDocument.filename}>
                  {selectedDocument.filename}
                </h3>
                <button
                  onClick={() => setSelectedDocument(null)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <span className="sr-only">Close</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="space-y-4">
                {loadingContent ? (
                  <div className="text-center py-8">
                    <p className="text-gray-500">Loading document content...</p>
                  </div>
                ) : selectedDocument.pages ? (
                  selectedDocument.pages.map((page) => (
                  <div key={page.page_number} className="border-t pt-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">
                      Page {page.page_number}
                    </h4>
                    <div className="space-y-2">
                      {page.paragraphs.map((paragraph) => (
                        <p key={paragraph.paragraph_number} className="text-sm text-gray-600">
                          {paragraph.content}
                        </p>
                      ))}
                    </div>
                  </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-500">No content available</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Search() {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState('hybrid');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState(null);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [loadingContent, setLoadingContent] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setSearching(true);
    setError(null);

    try {
      const searchResults = await searchDocuments(query, mode);
      setResults(searchResults);
    } catch (err) {
      setError(err.message);
    } finally {
      setSearching(false);
    }
  };

  const handleViewDocument = async (docId, pageNumber, paragraphNumber) => {
    setLoadingContent(true);
    try {
      const documentDetails = await getDocumentDetails(docId);
      setSelectedDocument({
        ...documentDetails,
        highlightPage: pageNumber,
        highlightParagraph: paragraphNumber
      });
    } catch (err) {
      setError('Failed to load document content');
    } finally {
      setLoadingContent(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Search Documents</h2>
      <div className="max-w-xl mx-auto">
        <div className="mt-1 relative rounded-md shadow-sm">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            className="focus:ring-primary-500 focus:border-primary-500 block w-full pl-4 pr-12 sm:text-sm border-gray-300 rounded-md"
            placeholder="Search your documents..."
          />
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            <button
              onClick={handleSearch}
              disabled={searching}
              className="text-primary-600 hover:text-primary-700 focus:outline-none"
            >
              <MagnifyingGlassIcon className="h-5 w-5" aria-hidden="true" />
            </button>
          </div>
        </div>

        <div className="mt-3 flex justify-center space-x-2">
          <button
            onClick={() => setMode('hybrid')}
            className={`px-3 py-1.5 text-sm font-medium rounded-md border transition-colors ${
              mode === 'hybrid'
                ? 'bg-primary-600 text-white border-primary-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }`}
          >
            Hybrid (dense + BM25)
          </button>
          <button
            onClick={() => setMode('dense')}
            className={`px-3 py-1.5 text-sm font-medium rounded-md border transition-colors ${
              mode === 'dense'
                ? 'bg-primary-600 text-white border-primary-600'
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
            }`}
          >
            Dense only
          </button>
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-50 rounded-md">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {searching && (
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600">Searching...</p>
          </div>
        )}

        {results.length > 0 && (
          <div className="mt-6 space-y-4">
            {results.map((result, index) => (
              <div key={index} className="bg-white shadow rounded-lg p-4">
                <p className="text-sm text-gray-900">{result.text}</p>
                <div className="mt-2 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <p className="text-xs text-gray-500">
                      Document ID: {result.metadata.doc_id}
                    </p>
                    {result.dense_score !== undefined && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-700">
                        dense {result.dense_score.toFixed(3)}
                      </span>
                    )}
                    {result.sparse_score !== undefined && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700">
                        bm25 {result.sparse_score.toFixed(3)}
                      </span>
                    )}
                    {result.sources && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                        {result.sources.join(', ')}
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => handleViewDocument(
                      result.metadata.doc_id,
                      result.metadata.page,
                      result.metadata.paragraph
                    )}
                    className="text-primary-600 hover:text-primary-700 text-sm"
                  >
                    View in Document →
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {!searching && results.length === 0 && query && (
          <div className="mt-4 text-center">
            <p className="text-sm text-gray-600">No results found</p>
          </div>
        )}
      </div>

      {/* Document View Modal */}
      {selectedDocument && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-medium text-gray-900 truncate max-w-2xl" title={selectedDocument.filename}>
                  {selectedDocument.filename}
                </h3>
                <button
                  onClick={() => setSelectedDocument(null)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <span className="sr-only">Close</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="space-y-4">
                {loadingContent ? (
                  <div className="text-center py-8">
                    <p className="text-gray-500">Loading document content...</p>
                  </div>
                ) : selectedDocument.pages ? (
                  selectedDocument.pages.map((page) => (
                    <div 
                      key={page.page_number} 
                      className={`border-t pt-4 ${page.page_number === selectedDocument.highlightPage ? 'bg-yellow-50' : ''}`}
                    >
                      <h4 className="text-sm font-medium text-gray-900 mb-2">
                        Page {page.page_number}
                      </h4>
                      <div className="space-y-2">
                        {page.paragraphs.map((paragraph) => (
                          <p 
                            key={paragraph.paragraph_number} 
                            className={`text-sm text-gray-600 ${
                              page.page_number === selectedDocument.highlightPage && 
                              paragraph.paragraph_number === selectedDocument.highlightParagraph 
                                ? 'bg-yellow-100 p-2 rounded' 
                                : ''
                            }`}
                          >
                            {paragraph.content}
                          </p>
                        ))}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-500">No content available</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function QA() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [loadingContent, setLoadingContent] = useState(false);

  const handleSubmit = async () => {
    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const result = await askQuestion(question);
      setAnswer(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDocument = async (docId, pageNumber, paragraphNumber) => {
    setLoadingContent(true);
    try {
      const documentDetails = await getDocumentDetails(docId);
      setSelectedDocument({
        ...documentDetails,
        highlightPage: pageNumber,
        highlightParagraph: paragraphNumber
      });
    } catch (err) {
      setError('Failed to load document content');
    } finally {
      setLoadingContent(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-4">Ask Questions</h2>
      <div className="max-w-xl mx-auto">
        <div className="mt-1">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={4}
            className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
            placeholder="Ask a question about your documents..."
          />
        </div>
        <div className="mt-3">
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            {loading ? 'Getting Answer...' : 'Submit Question'}
          </button>
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-50 rounded-md">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {answer && (
          <div className="mt-6 space-y-4">
            {answer.map((item, index) => (
              <div key={index} className="bg-white shadow rounded-lg p-4">
                <p className="text-sm font-medium text-gray-900">{item.doc_id}</p>
                <p className="mt-2 text-sm text-gray-600">{item.content}</p>
                {item.page && item.paragraph && (
                  <div className="mt-2 flex items-center justify-between">
                    <p className="text-xs text-gray-500">
                      Page {item.page} • Paragraph {item.paragraph}
                    </p>
                    <button
                      onClick={() => handleViewDocument(item.doc_id, item.page, item.paragraph)}
                      className="text-primary-600 hover:text-primary-700 text-sm"
                    >
                      View in Document →
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Document View Modal */}
      {selectedDocument && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-medium text-gray-900 truncate max-w-2xl" title={selectedDocument.filename}>
                  {selectedDocument.filename}
                </h3>
                <button
                  onClick={() => setSelectedDocument(null)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <span className="sr-only">Close</span>
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="space-y-4">
                {loadingContent ? (
                  <div className="text-center py-8">
                    <p className="text-gray-500">Loading document content...</p>
                  </div>
                ) : selectedDocument.pages ? (
                  selectedDocument.pages.map((page) => (
                    <div 
                      key={page.page_number} 
                      className={`border-t pt-4 ${page.page_number === selectedDocument.highlightPage ? 'bg-yellow-50' : ''}`}
                    >
                      <h4 className="text-sm font-medium text-gray-900 mb-2">
                        Page {page.page_number}
                      </h4>
                      <div className="space-y-2">
                        {page.paragraphs.map((paragraph) => (
                          <p 
                            key={paragraph.paragraph_number} 
                            className={`text-sm text-gray-600 ${
                              page.page_number === selectedDocument.highlightPage && 
                              paragraph.paragraph_number === selectedDocument.highlightParagraph 
                                ? 'bg-yellow-100 p-2 rounded' 
                                : ''
                            }`}
                          >
                            {paragraph.content}
                          </p>
                        ))}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-500">No content available</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Evaluate() {
  const [mode, setMode] = useState('retrieval');
  const [k, setK] = useState(5);
  const [testCases, setTestCases] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const metricLabels = {
    recall: 'Recall@k',
    precision: 'Precision@k',
    mrr: 'MRR',
    ndcg: 'NDCG@k',
    hit_rate: 'Hit Rate@k',
  };

  const handleRun = async () => {
    setError(null);
    setLoading(true);
    try {
      const parsed = JSON.parse(testCases || '[]');
      if (!Array.isArray(parsed) || parsed.length === 0) {
        throw new Error('Enter at least one test case as a JSON array');
      }
      const data = mode === 'retrieval'
        ? await evaluateRetrieval(parsed, k)
        : await evaluateGeneration(parsed, k);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-1">Evaluate RAG Quality</h2>
      <p className="text-sm text-gray-600 mb-6">
        Run metric-driven tests against the retrieval and generation pipeline to measure quality.
      </p>

      <div className="mb-4 flex space-x-2">
        <button
          onClick={() => { setMode('retrieval'); setResult(null); }}
          className={`px-4 py-2 text-sm font-medium rounded-md border transition-colors ${
            mode === 'retrieval'
              ? 'bg-primary-600 text-white border-primary-600'
              : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
          }`}
        >
          Retrieval (Recall@k, MRR, NDCG)
        </button>
        <button
          onClick={() => { setMode('generation'); setResult(null); }}
          className={`px-4 py-2 text-sm font-medium rounded-md border transition-colors ${
            mode === 'generation'
              ? 'bg-primary-600 text-white border-primary-600'
              : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
          }`}
        >
          Generation (Faithfulness, Relevance)
        </button>
      </div>

      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Test cases (JSON array)
        </label>
        <textarea
          rows={8}
          value={testCases}
          onChange={(e) => setTestCases(e.target.value)}
          placeholder={mode === 'retrieval' ? 'Retrieval: each case needs "question" and "relevant_chunk_ids".' : 'Generation: each case needs "question" and optional "reference_answer".'}
          className="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md font-mono"
        />
        <p className="mt-2 text-xs text-gray-500">
          Chunk ids follow the pattern <span className="font-mono">docId_p{'{page}'}_c{'{num}'}</span>. Tip: use the
          document details view to find page/paragraph references.
        </p>
        <div className="mt-4 flex items-center space-x-4">
          <button
            onClick={handleRun}
            disabled={loading}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            {loading ? 'Running...' : 'Run Evaluation'}
          </button>
          <span className="flex items-center space-x-2 text-sm text-gray-600">
            <span>Top-{k}</span>
            <input
              type="range"
              min="1"
              max="20"
              value={k}
              onChange={(e) => setK(Number(e.target.value))}
              className="w-32"
            />
          </span>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 rounded-md">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {result && mode === 'retrieval' && (
        <>
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Averaged Retrieval Metrics</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {Object.entries(result.averages).map(([key, value]) => (
                <div key={key} className="bg-gray-50 rounded-lg p-4 text-center">
                  <p className="text-2xl font-bold text-primary-600">{(value * 100).toFixed(1)}%</p>
                  <p className="text-xs text-gray-500 mt-1">{metricLabels[key] || key}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Per-question breakdown</h3>
            <div className="space-y-4">
              {result.per_question.map((item, idx) => (
                <div key={idx} className="border border-gray-200 rounded-lg p-4">
                  <p className="text-sm font-medium text-gray-900">{item.question}</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {Object.entries(item.metrics).map(([k2, v]) => (
                      <span key={k2} className="inline-flex items-center px-2 py-1 rounded bg-gray-100 text-xs text-gray-700">
                        {metricLabels[k2] || k2}: {(v * 100).toFixed(0)}%
                      </span>
                    ))}
                  </div>
                  <details className="mt-3">
                    <summary className="text-xs text-primary-600 hover:text-primary-500 cursor-pointer">
                      Retrieved chunk ids
                    </summary>
                    <pre className="mt-2 text-xs font-mono text-gray-600 bg-gray-50 rounded p-3 overflow-x-auto">
                      {item.retrieved_chunk_ids.join('\n')}
                    </pre>
                  </details>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {result && mode === 'generation' && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Generation Quality</h3>
          <div className="space-y-4">
            {result.results.map((item, idx) => (
              <div key={idx} className="border border-gray-200 rounded-lg p-4">
                <p className="text-sm font-medium text-gray-900">{item.question}</p>
                <p className="mt-2 text-sm text-gray-600">
                  <span className="font-medium">Answer:</span> {item.answer}
                </p>
                <div className="mt-3 grid grid-cols-2 gap-3">
                  <div className="bg-gray-50 rounded-lg p-3 text-center">
                    <p className="text-2xl font-bold text-primary-600">
                      {(item.metrics.faithfulness * 100).toFixed(1)}%
                    </p>
                    <p className="text-xs text-gray-500 mt-1">Faithfulness (context grounded)</p>
                  </div>
                  <div className="bg-gray-50 rounded-lg p-3 text-center">
                    <p className="text-2xl font-bold text-primary-600">
                      {(item.metrics.answer_relevance * 100).toFixed(1)}%
                    </p>
                    <p className="text-xs text-gray-500 mt-1">Answer Relevance</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;