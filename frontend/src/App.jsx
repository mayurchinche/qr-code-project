import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./components/pages/Home";
import AdminPage from "./components/AdminPage";
import InvoiceViewer from "./components/InvoiceViewer";
const API_URL = import.meta.env.VITE_API_URL;
console.log("Backend API:", API_URL);

export default function App() {
    return (
        <Router>
            <Routes>
                <Route path="/:model_name/:serial_number" element={<HomePage />} />
                <Route path="/invoice-viewer" element={<InvoiceViewer />} />
                <Route path="/admin" element={<AdminPage />} />

            </Routes>
        </Router>
    );
}
