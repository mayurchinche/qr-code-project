import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { CircularProgress, Container } from "@mui/material";

export default function InvoiceViewer() {
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const fileId = queryParams.get("file_id");  // Get File ID from URL
    const [pdfBlob, setPdfBlob] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPdf = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:8000/download_pdf/?file_id=${fileId}`);
                if (!response.ok) throw new Error("Failed to fetch PDF");

                const blob = await response.blob();
                setPdfBlob(URL.createObjectURL(blob));
            } catch (error) {
                console.error("Error fetching PDF:", error);
            } finally {
                setLoading(false);
            }
        };

        if (fileId) {
            fetchPdf();
        }
    }, [fileId]);

    if (loading) {
        return <Container style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}><CircularProgress /></Container>;
    }

    if (!pdfBlob) {
        return <Container style={{ textAlign: "center", padding: "20px" }}>Failed to load PDF</Container>;
    }

    return (
        <div style={{
            width: "100vw",
            height: "100vh",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            backgroundColor: "#f5f5f5"
        }}>
            <iframe
                src={pdfBlob}
                width="80%"
                height="90%"
                style={{ border: "none" }}
                allowFullScreen
            />
        </div>
    );
}
