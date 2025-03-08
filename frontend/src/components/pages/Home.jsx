import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { TextField, Button, Card, CardContent, CardHeader, Typography, Grid, Container } from "@mui/material";
import { toast } from "react-hot-toast";

export default function HomePage() {
    const { model_name, serial_number } = useParams();
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [company, setCompany] = useState("");
    const [city, setCity] = useState("");
    const [model, setModel] = useState(model_name || "");
    const [serial, setSerial] = useState(serial_number || "");

    const handleSubmit = async () => {
        if (!email || !company || !city) {
            toast.error("Please fill in all required fields.");
            return;
        }

        try {
            const response = await fetch("http://127.0.0.1:8000/submit_form", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: new URLSearchParams({ email, company, city, model, serial })
            });
            const data = await response.json();
            if (data.redirect_url) {
                navigate(`/invoice-viewer?url=${encodeURIComponent(data.redirect_url.invoice_url)}`);
            } else {
                toast.error("Failed to submit form. Please try again.");
            }
        } catch (error) {
            console.error("Error submitting form:", error);
            toast.error("Server error. Please check the backend.");
        }
    };

    return (
        <Container maxWidth="md" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f5f5f5', padding: '20px' }}>
            <Card style={{ width: '100%', maxWidth: '600px', padding: '20px', backgroundColor: '#ffffff', boxShadow: '0px 4px 10px rgba(0,0,0,0.2)', borderRadius: '12px', textAlign: 'center' }}>
                <CardHeader title={<Typography variant="h5" align="center">User Information</Typography>} />
                <CardContent>
                    <Grid container spacing={2}>
                        <Grid item xs={12}>
                            <TextField label="Email" variant="outlined" value={email} onChange={(e) => setEmail(e.target.value)} fullWidth required />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField label="Company Name" variant="outlined" value={company} onChange={(e) => setCompany(e.target.value)} fullWidth required />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField label="City" variant="outlined" value={city} onChange={(e) => setCity(e.target.value)} fullWidth required />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField label="Model Name" variant="outlined" value={model} fullWidth disabled />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField label="Serial Number" variant="outlined" value={serial} fullWidth disabled />
                        </Grid>
                        <Grid item xs={12}>
                            <Button variant="contained" color="primary" onClick={handleSubmit} fullWidth>
                                Submit
                            </Button>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>
        </Container>
    );
}

export function InvoiceViewer() {
    const [pdfUrl, setPdfUrl] = useState(null);
    const navigate = useNavigate();
    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const url = params.get("url");
        if (url) {
            setPdfUrl(url);
        } else {
            toast.error("Invalid PDF URL");
            navigate("/");
        }
    }, [navigate]);

    return (
        <Container maxWidth="lg" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f5f5f5', padding: '20px' }}>
            <Card style={{ width: '100%', maxWidth: '800px', padding: '20px', backgroundColor: '#ffffff', boxShadow: '0px 4px 10px rgba(0,0,0,0.2)', borderRadius: '12px', textAlign: 'center' }}>
                <CardHeader title={<Typography variant="h5" align="center">Invoice Viewer</Typography>} />
                <CardContent>
                    {pdfUrl ? (
                        <iframe src={pdfUrl} title="Invoice PDF" width="100%" height="600px" style={{ border: 'none' }} />
                    ) : (
                        <Typography variant="body1">Loading PDF...</Typography>
                    )}
                </CardContent>
            </Card>
        </Container>
    );
}
