import { useState } from "react";
import { TextField, Button, Card, CardContent, CardHeader, Typography, Grid, Container } from "@mui/material";
import { toast } from "react-hot-toast";

export default function AdminPage() {

    console.log("Admin Page");

    const [model, setModel] = useState("");
    const [serial, setSerial] = useState("");
    const [qrCode, setQrCode] = useState(null);
    const [qrUrl, setQrUrl] = useState(null);

    const generateQRCode = async () => {
        if (!model || !serial) {
            toast.error("Please enter both Model Name and Serial Number.");
            return;
        }

        try {

            const response = await fetch(`{API_URL}/generate_qr?model_name=${model}&serial_number=${serial}`);
            const data = await response.json();

            if (data.qr_code && data.url) {
                setQrCode(data.qr_code);
                setQrUrl(data.url);
                toast.success("QR Code generated successfully!");
            } else {
                toast.error("Failed to generate QR Code. Please try again.");
            }
        } catch (error) {
            console.error("Error generating QR Code:", error);
            toast.error("Server error. Please check the backend.");
        }
    };

    const printQRCode = () => {
        if (qrCode) {
            const newWindow = window.open();
            newWindow.document.write(`
                <html>
                    <head>
                        <title>Print QR Code</title>
                    </head>
                    <body style="background-color: white; display: flex; align-items: center; justify-content: center; height: 100vh;">
                        <img src="${qrCode}" alt="QR Code" style="width: 300px; height: 300px;" />
                        <script>window.onload = function() { window.print(); }</script>
                    </body>
                </html>
            `);
            newWindow.document.close();
        }
    };

    return (
        <Container maxWidth="md" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f5f5f5', padding: '20px' }}>
            <Card style={{ width: '100%', maxWidth: '600px', padding: '20px', backgroundColor: '#ffffff', boxShadow: '0px 4px 10px rgba(0,0,0,0.2)', borderRadius: '12px', textAlign: 'center' }}>
                <CardHeader title={<Typography variant="h5" align="center">Admin - Generate QR Code</Typography>} />
                <CardContent>
                    <Grid container spacing={2}>
                        <Grid item xs={12}>
                            <TextField
                                label="Model Name"
                                variant="outlined"
                                value={model}
                                onChange={(e) => setModel(e.target.value)}
                                fullWidth
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <TextField
                                label="Serial Number"
                                variant="outlined"
                                value={serial}
                                onChange={(e) => setSerial(e.target.value)}
                                fullWidth
                            />
                        </Grid>
                        <Grid item xs={12}>
                            <Button variant="contained" color="primary" onClick={generateQRCode} fullWidth>
                                Generate QR Code
                            </Button>
                        </Grid>
                        {qrCode && (
                            <Grid item xs={12}>
                                <Typography variant="h6" style={{ marginBottom: '10px' }}>QR Code Generated:</Typography>
                                <img src={qrCode} alt="Generated QR Code" style={{ width: '200px', height: '200px' }} />
                                <Typography variant="body2" style={{ marginTop: '10px', color: '#3f51b5', textDecoration: 'underline' }}>
                                    <a href={qrUrl} target="_blank" rel="noopener noreferrer">Open Form Page</a>
                                </Typography>
                                <Button variant="outlined" color="secondary" onClick={printQRCode} style={{ marginTop: '15px' }}>
                                    Print QR Code
                                </Button>
                            </Grid>
                        )}
                    </Grid>
                </CardContent>
            </Card>
        </Container>
    );
}
