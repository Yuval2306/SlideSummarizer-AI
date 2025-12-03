import React, { useState } from "react";
import { jsPDF } from "jspdf";

const API_URL = "https://slidesummarizer-backend.onrender.com";

// Summary level configurations
const SUMMARY_LEVELS = {
  beginner: {
    label: "📖 Beginner-Friendly",
    description: "Simple and clear explanation",
    color: "#FF6B9D",
    bgColor: "#FFE8F0",
  },
  comprehensive: {
    label: "📊 Comprehensive Analysis",
    description: "Detailed and thorough",
    color: "#4ECDC4",
    bgColor: "#E0F7F6",
  },
  executive: {
    label: "⚡ Executive Brief",
    description: "Quick and concise",
    color: "#FFD93D",
    bgColor: "#FFF9E6",
  },
};

// Language configurations
const LANGUAGES = {
  en: { label: "🇺🇸 English", code: "en" },
  he: { label: "🇮🇱 Hebrew", code: "he" },
  ru: { label: "🇷🇺 Russian", code: "ru" },
  es: { label: "🇪🇸 Spanish", code: "es" },
};

function App() {
  const [file, setFile] = useState(null);
  const [summaryLevel, setSummaryLevel] = useState("comprehensive");
  const [language, setLanguage] = useState("en");
  const [uploadUid, setUploadUid] = useState("");
  const [statusText, setStatusText] = useState("");
  const [loading, setLoading] = useState(false);
  const [explanations, setExplanations] = useState([]);
  const [error, setError] = useState("");

  // Upload PPTX to backend
  const uploadFile = async () => {
    if (!file) {
      setError("Please select a file first");
      return;
    }

    setLoading(true);
    setError("");
    setStatusText("Uploading presentation...");

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("email", "test@example.com");
      formData.append("summary_level", summaryLevel);
      formData.append("language", language);

      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errBody = await response.json().catch(() => ({}));
        throw new Error(errBody.error || "Upload failed");
      }

      const data = await response.json();
      const uid = data.uid;

      setUploadUid(uid);
      setStatusText("✅ File uploaded - Processing with AI...");
      await pollStatus(uid);
    } catch (err) {
      setError(err.message || "Upload failed");
      setStatusText("");
    } finally {
      setLoading(false);
    }
  };

  // Poll backend until processing is done
  const pollStatus = async (uid) => {
    setLoading(true);
    const levelLabel = SUMMARY_LEVELS[summaryLevel].label;
    setStatusText(`⏳ Processing slides (${levelLabel})...`);

    try {
      while (true) {
        const resp = await fetch(`${API_URL}/status/${uid}`);
        if (!resp.ok) throw new Error("Server error while checking status");

        const data = await resp.json();

        if (data.status === "completed") {
          setStatusText("✨ Processing completed successfully!");
          setExplanations(data.explanation || []);
          setError("");
          break;
        }

        if (data.status === "failed") {
          setError(data.error_message || "Processing failed");
          setStatusText("");
          break;
        }

        await new Promise((resolve) => setTimeout(resolve, 2000));
      }
    } catch (err) {
      setError(err.message || "Status check failed");
      setStatusText("");
    } finally {
      setLoading(false);
    }
  };

  // Create PDF file with explanations
  const downloadPdf = () => {
    if (explanations.length === 0) {
      setError("No explanations to export");
      return;
    }

    const doc = new jsPDF();
    let y = 20;
    const marginLeft = 15;
    const levelLabel = SUMMARY_LEVELS[summaryLevel].label;
    const langLabel = LANGUAGES[language].label;

    doc.setFont("helvetica", "bold");
    doc.setFontSize(18);
    doc.text("Slide Explanations Summary", marginLeft, y);
    y += 8;

    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.text(`Level: ${levelLabel} | Language: ${langLabel}`, marginLeft, y);
    y += 12;

    explanations.forEach((item, index) => {
      const slideNumber =
        item.slide_number != null ? item.slide_number : index + 1;
      const title = `Slide ${slideNumber}`;
      const text = (item.explanation || "").replace(/\r\n/g, "\n");

      if (y > 260) {
        doc.addPage();
        y = 20;
      }

      doc.setFont("helvetica", "bold");
      doc.setFontSize(14);
      doc.text(title, marginLeft, y);
      y += 8;

      doc.setFont("helvetica", "normal");
      doc.setFontSize(11);
      const lines = doc.splitTextToSize(text, 180);

      lines.forEach((line) => {
        if (y > 280) {
          doc.addPage();
          y = 20;
        }
        doc.text(line, marginLeft, y);
        y += 6;
      });

      y += 5;
    });

    doc.save("slides_explanations.pdf");
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        padding: "20px",
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
      }}
    >
      <div
        style={{
          maxWidth: "1100px",
          margin: "0 auto",
        }}
      >
        {/* Header */}
        <div
          style={{
            textAlign: "center",
            marginBottom: "40px",
            color: "#fff",
          }}
        >
          <h1
            style={{
              fontSize: "48px",
              fontWeight: "700",
              margin: "0 0 10px 0",
              letterSpacing: "-1px",
            }}
          >
            Slide Explainer Pro
          </h1>
          <p style={{ fontSize: "16px", opacity: 0.95, margin: "0" }}>
            Transform your presentations with AI-powered insights
          </p>
        </div>

        {/* Main Card */}
        <div
          style={{
            background: "#fff",
            borderRadius: "20px",
            boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
            padding: "40px",
            marginBottom: "20px",
          }}
        >
          {/* File Upload Section */}
          <div
            style={{
              background: "linear-gradient(135deg, #667eea15 0%, #764ba215 100%)",
              border: "2px dashed #667eea",
              borderRadius: "12px",
              padding: "30px",
              textAlign: "center",
              marginBottom: "30px",
            }}
          >
            <div style={{ fontSize: "32px", marginBottom: "10px" }}>📄</div>
            <label
              style={{
                display: "block",
                cursor: "pointer",
                fontSize: "16px",
                fontWeight: "600",
                color: "#333",
                marginBottom: "8px",
              }}
            >
              Choose a PowerPoint file
            </label>
            <input
              type="file"
              accept=".ppt,.pptx"
              onChange={(e) => {
                setFile(e.target.files[0]);
                setExplanations([]);
                setUploadUid("");
                setError("");
                setStatusText("");
              }}
              style={{
                display: "none",
              }}
              id="file-input"
            />
            <label
              htmlFor="file-input"
              style={{
                display: "inline-block",
                background: "#667eea",
                color: "#fff",
                padding: "10px 24px",
                borderRadius: "8px",
                cursor: "pointer",
                fontWeight: "600",
                transition: "all 0.3s ease",
              }}
              onMouseEnter={(e) => {
                e.target.style.background = "#5568d3";
                e.target.style.transform = "translateY(-2px)";
              }}
              onMouseLeave={(e) => {
                e.target.style.background = "#667eea";
                e.target.style.transform = "translateY(0)";
              }}
            >
              Browse Files
            </label>
            {file && (
              <p style={{ marginTop: "10px", fontSize: "14px", color: "#666" }}>
                ✅ Selected: <strong>{file.name}</strong>
              </p>
            )}
          </div>

          {/* Language Selection */}
          <div style={{ marginBottom: "30px" }}>
            <h3
              style={{
                fontSize: "16px",
                fontWeight: "700",
                color: "#333",
                marginBottom: "12px",
              }}
            >
              🌍 Select Language
            </h3>
            <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
              {Object.entries(LANGUAGES).map(([key, { label }]) => (
                <button
                  key={key}
                  onClick={() => setLanguage(key)}
                  disabled={loading}
                  style={{
                    background:
                      language === key
                        ? "#667eea"
                        : "#f0f0f0",
                    color: language === key ? "#fff" : "#333",
                    border: "none",
                    padding: "12px 18px",
                    borderRadius: "8px",
                    cursor: loading ? "default" : "pointer",
                    fontWeight: language === key ? "700" : "600",
                    fontSize: "14px",
                    transition: "all 0.3s ease",
                  }}
                  onMouseEnter={(e) => {
                    if (!loading && language !== key) {
                      e.target.style.background = "#e0e0e0";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!loading && language !== key) {
                      e.target.style.background = "#f0f0f0";
                    }
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Summary Level Selection */}
          <div style={{ marginBottom: "30px" }}>
            <h3
              style={{
                fontSize: "16px",
                fontWeight: "700",
                color: "#333",
                marginBottom: "12px",
              }}
            >
              📋 Select Summary Level
            </h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
                gap: "12px",
              }}
            >
              {Object.entries(SUMMARY_LEVELS).map(
                ([key, { label, description, color, bgColor }]) => (
                  <button
                    key={key}
                    onClick={() => setSummaryLevel(key)}
                    disabled={loading}
                    style={{
                      background:
                        summaryLevel === key
                          ? bgColor
                          : "#f5f5f5",
                      border:
                        summaryLevel === key
                          ? `2px solid ${color}`
                          : "2px solid #e0e0e0",
                      padding: "16px",
                      borderRadius: "12px",
                      cursor: loading ? "default" : "pointer",
                      transition: "all 0.3s ease",
                      textAlign: "left",
                    }}
                    onMouseEnter={(e) => {
                      if (!loading) {
                        e.currentTarget.style.transform = "translateY(-4px)";
                        e.currentTarget.style.boxShadow =
                          "0 10px 20px rgba(0,0,0,0.1)";
                      }
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = "translateY(0)";
                      e.currentTarget.style.boxShadow = "none";
                    }}
                  >
                    <div
                      style={{
                        fontSize: "16px",
                        fontWeight: "700",
                        color: summaryLevel === key ? color : "#333",
                        marginBottom: "4px",
                      }}
                    >
                      {label}
                    </div>
                    <div
                      style={{
                        fontSize: "13px",
                        color: summaryLevel === key ? "#555" : "#999",
                      }}
                    >
                      {description}
                    </div>
                  </button>
                )
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: "flex", gap: "12px", marginBottom: "20px" }}>
            <button
              onClick={uploadFile}
              disabled={loading || !file}
              style={{
                background: loading || !file ? "#ccc" : "#667eea",
                color: "#fff",
                border: "none",
                padding: "14px 32px",
                borderRadius: "10px",
                fontWeight: "700",
                fontSize: "16px",
                cursor: loading || !file ? "default" : "pointer",
                transition: "all 0.3s ease",
                boxShadow:
                  loading || !file
                    ? "none"
                    : "0 4px 15px rgba(102, 126, 234, 0.4)",
              }}
              onMouseEnter={(e) => {
                if (!loading && file) {
                  e.target.style.background = "#5568d3";
                  e.target.style.transform = "translateY(-2px)";
                }
              }}
              onMouseLeave={(e) => {
                if (!loading && file) {
                  e.target.style.background = "#667eea";
                  e.target.style.transform = "translateY(0)";
                }
              }}
            >
              {loading ? "⏳ Processing..." : "🚀 Upload & Analyze"}
            </button>

            <button
              onClick={downloadPdf}
              disabled={explanations.length === 0}
              style={{
                background:
                  explanations.length === 0 ? "#ccc" : "#10b981",
                color: "#fff",
                border: "none",
                padding: "14px 32px",
                borderRadius: "10px",
                fontWeight: "700",
                fontSize: "16px",
                cursor:
                  explanations.length === 0
                    ? "default"
                    : "pointer",
                transition: "all 0.3s ease",
                boxShadow:
                  explanations.length === 0
                    ? "none"
                    : "0 4px 15px rgba(16, 185, 129, 0.4)",
              }}
              onMouseEnter={(e) => {
                if (explanations.length > 0) {
                  e.target.style.background = "#059669";
                  e.target.style.transform = "translateY(-2px)";
                }
              }}
              onMouseLeave={(e) => {
                if (explanations.length > 0) {
                  e.target.style.background = "#10b981";
                  e.target.style.transform = "translateY(0)";
                }
              }}
            >
              📥 Download PDF
            </button>
          </div>

          {/* Status Messages */}
          {uploadUid && (
            <p style={{ fontSize: "12px", color: "#999", margin: "8px 0" }}>
              Upload ID: <code style={{ background: "#f5f5f5", padding: "2px 6px", borderRadius: "4px" }}>{uploadUid}</code>
            </p>
          )}

          {statusText && (
            <p
              style={{
                color: "#667eea",
                fontWeight: "600",
                margin: "8px 0",
                fontSize: "15px",
              }}
            >
              {statusText}
            </p>
          )}

          {error && (
            <p style={{ color: "#e63946", fontWeight: "600", margin: "8px 0" }}>
              ❌ {error}
            </p>
          )}
        </div>

        {/* Explanations Grid */}
        {explanations.length > 0 && (
          <div>
            <h2
              style={{
                color: "#fff",
                fontSize: "24px",
                fontWeight: "700",
                marginBottom: "16px",
              }}
            >
              {SUMMARY_LEVELS[summaryLevel].label}
            </h2>

            <div
              style={{
                display: "grid",
                gap: "16px",
                gridTemplateColumns:
                  "repeat(auto-fill, minmax(320px, 1fr))",
              }}
            >
              {explanations.map((item, idx) => (
                <div
                  key={idx}
                  style={{
                    background: "#fff",
                    borderRadius: "16px",
                    padding: "20px",
                    border: `3px solid ${
                      SUMMARY_LEVELS[summaryLevel].color
                    }`,
                    boxShadow: "0 8px 24px rgba(0,0,0,0.12)",
                    transition: "all 0.3s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = "translateY(-4px)";
                    e.currentTarget.style.boxShadow =
                      "0 12px 32px rgba(0,0,0,0.18)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = "translateY(0)";
                    e.currentTarget.style.boxShadow =
                      "0 8px 24px rgba(0,0,0,0.12)";
                  }}
                >
                  <h3
                    style={{
                      margin: "0 0 12px 0",
                      color:
                        SUMMARY_LEVELS[summaryLevel].color,
                      fontSize: "16px",
                      fontWeight: "700",
                    }}
                  >
                    Slide {item.slide_number}
                  </h3>
                  <p
                    style={{
                      whiteSpace: "pre-wrap",
                      margin: 0,
                      lineHeight: "1.6",
                      color: "#555",
                      fontSize: "14px",
                    }}
                  >
                    {item.explanation}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;