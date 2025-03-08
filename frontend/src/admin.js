import { useState } from "react";
import { TextField, Button, Card, CardContent, CardHeader, Typography } from "@mui/material";
import { toast } from "react-hot-toast";

export default function AdminPage() {
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
            const response = await fetch(`http://127.0.0.1:8000/generate_qr?model_name=${model}&serial_number=${serial}`);
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
                    <body>
                        <img src="${qrCode}" alt="QR Code" style="width: 300px; height: 300px;" />
                        <script>window.onload = function() { window.print(); }</script>
                    </body>
                </html>
            `);
            newWindow.document.close();
        }
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', background: 'linear-gradient(to right, #3f51b5, #9c27b0)', padding: '20px', color: 'white' }}>
            <Card style={{ width: '100%', maxWidth: '400px', padding: '20px', backgroundColor: 'white', color: 'black', boxShadow: '0px 4px 10px rgba(0,0,0,0.2)', borderRadius: '12px' }}>
                <CardHeader title={<Typography variant="h5" align="center">Admin - Generate QR Code</Typography>} />
                <CardContent style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                    <TextField
                        label="Model Name"
                        variant="outlined"
                        value={model}
                        onChange={(e) => setModel(e.target.value)}
                        fullWidth
                    />
                    <TextField
                        label="Serial Number"
                        variant="outlined"
                        value={serial}
                        onChange={(e) => setSerial(e.target.value)}
                        fullWidth
                    />
                    <Button variant="contained" color="primary" onClick={generateQRCode} fullWidth>
                        Generate QR Code
                    </Button>
                    {qrCode && (
                        <div style={{ textAlign: 'center' }}>
                            <Typography variant="h6" style={{ marginBottom: '10px' }}>QR Code Generated:</Typography>
                            <img src={qrCode} alt="Generated QR Code" style={{ width: '200px', height: '200px', margin: '0 auto' }} />
                            <Typography variant="body2" style={{ marginTop: '10px', color: '#3f51b5', textDecoration: 'underline' }}>
                                <a href={qrUrl} target="_blank" rel="noopener noreferrer">Open Form Page</a>
                            </Typography>
                            <Button variant="outlined" color="secondary" onClick={printQRCode} style={{ marginTop: '15px' }}>
                                Print QR Code
                            </Button>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
