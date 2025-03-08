import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import HomePage from "./components/pages/Home";
import AdminPage from "./components/AdminPage";
import InvoiceViewer from "./components/InvoiceViewer";

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
