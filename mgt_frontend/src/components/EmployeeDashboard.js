import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { NavLink, useNavigate } from 'react-router-dom'; // Updated: useNavigate
import api from "../api";

// Styled components
const DashboardContainer = styled.div`
  padding: 2rem;
  background-color: #f8f3ef;
  min-height: 100vh;
`;

const Section = styled.section`
  background-color: #f0f4f9;
  padding: 2rem;
  margin-bottom: 2rem;
  border-radius: 16px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
`;

const Title = styled.h2`
  color: #333;
`;

const Label = styled.label`
  margin: 0.5rem 0;
  font-size: 1rem;
  color: #333;
`;

const InputFile = styled.input`
  padding: 0.8rem;
  margin-top: 1rem;
  font-size: 1rem;
`;

const InputText = styled.input`
  padding: 0.8rem;
  margin-top: 1rem;
  font-size: 1rem;
  border-radius: 8px;
  border: 1px solid #ddd;
`;

const Button = styled.button`
  padding: 0.9rem;
  background-color: #0474c4;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  width: 100%;
  margin-top: 1rem;

  &:hover {
    background-color: #045bb5;
  }
`;

const UploadMessage = styled.p`
  margin-top: 1rem;
  font-size: 1rem;
  color: ${(props) => (props.success ? '#47a47d' : '#ff3b3b')};
`;

const StatusSection = styled(Section)`
  background-color: #f0f4f9;
`;


const Table = styled.table`
  width: 100%;
  margin-top: 1rem;
  border-collapse: collapse;
`;

const Th = styled.th`
  text-align: left;
  padding: 1rem;
  background-color: #0474c4;
  color: white;
  font-weight: bold;
`;

const Td = styled.td`
  padding: 1rem;
  border-bottom: 1px solid #ddd;
`;

const InputSearch = styled.input`
  padding: 0.8rem;
  margin-top: 1rem;
  font-size: 1rem;
  border-radius: 8px;
  width: 100%;
  border: 1px solid #ddd;
`;

const NavBar = styled.nav`
  background-color: #0474c4;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
`;

const NavTitle = styled.h1`
  margin: 0;
  font-size: 1.5rem;
`;

const LogoutButton = styled.button`
  background-color: #ff4b5c;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;

  &:hover {
    background-color: #d13a4a;
  }
`;

// EmployeeDashboard Component
const EmployeeDashboard = () => {
  const navigate = useNavigate(); // Updated: useNavigate replaces useHistory
  const [file, setFile] = useState(null);
  const [documentName, setDocumentName] = useState("");
  const [uploadMessage, setUploadMessage] = useState("");
  const [isUploadSuccess, setIsUploadSuccess] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredDocuments, setFilteredDocuments] = useState([]);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_id");
    navigate("/");
  };
  

  const fetchDocuments = async () => {
    try {
      const response = await api.get("/documents/documents/", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
      // Backend now filters documents for the logged-in user
      setDocuments(response.data);
      setFilteredDocuments(response.data);
    } catch (err) {
      console.error("Error fetching documents:", err);
    }
  };
  

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const uploadDocument = async (e) => {
    e.preventDefault();
    if (!file || !documentName.trim()) {
      setUploadMessage("File and title are required.");
      setIsUploadSuccess(false);
      return;
    }

    const formData = new FormData();
    formData.append("file_path", file);
    formData.append("title", documentName.trim());
    formData.append("status", "Submitted");

    try {
      const response = await api.post("/documents/documents/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      if (response.status === 201 || response.status === 200) {
        setUploadMessage("Document uploaded successfully!");
        setIsUploadSuccess(true);
        fetchDocuments();
      }
    } catch (error) {
      console.error("Upload failed:", error.response?.data || error.message);
      setUploadMessage("Failed to upload document. Check your inputs.");
      setIsUploadSuccess(false);
    }
  };

  const filterDocuments = () => {
    const filtered = documents.filter((doc) =>
      doc.title.toLowerCase().includes(searchQuery.toLowerCase())
    );
    setFilteredDocuments(filtered);
  };

  const handleViewDocument = (docId) => {
    alert(`Viewing document with ID: ${docId}`);
  };

  return (
    <DashboardContainer>
      {/* Navigation Bar */}
      <NavBar>
        <NavTitle>Employee Dashboard</NavTitle>
        <LogoutButton onClick={handleLogout}>Logout</LogoutButton>
      </NavBar>

      {/* Upload Section */}
      <Section>
        <Title>Upload Document</Title>
        <form onSubmit={uploadDocument}>
          <Label>Document Name</Label>
          <InputText
            type="text"
            value={documentName}
            onChange={(e) => setDocumentName(e.target.value)}
          />
          <Label>Select Document</Label>
          <InputFile type="file" onChange={handleFileChange} />
          <Button type="submit">Upload</Button>
          {uploadMessage && <UploadMessage>{uploadMessage}</UploadMessage>}
        </form>
      </Section>

      {/* Document Status Section */}
      <StatusSection>
        <Title>Document Status</Title>
        <InputSearch
          type="text"
          placeholder="Search by document title"
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            filterDocuments();
          }}
        />

        {filteredDocuments.length > 0 ? (
          <Table>
            <thead>
              <tr>
                <Th>Document Title</Th>
                <Th>File</Th>
                <Th>Type</Th>
                <Th>Status</Th>
                <Th>Actions</Th>
              </tr>
            </thead>
            <tbody>
              {filteredDocuments.map((doc) => (
                <tr key={doc.id}>
                  <Td>{doc.title}</Td>
                  <Td>{doc.file_path.split("/").pop()}</Td>
                  <Td>{doc.type || "N/A"}</Td>
                  <Td>{doc.status}</Td>
                  <Td>{doc.workflow_status || "No Workflow Instance"}</Td> {/* Display workflow instance status */}
                  <Td>
                    <Button onClick={() => handleViewDocument(doc.id)}>
                      View
                    </Button>
                  </Td>
                </tr>
              ))}
            </tbody>
          </Table>
        ) : (
          <p>No documents found matching your search.</p>
        )}
      </StatusSection>
    </DashboardContainer>
  );
};

export default EmployeeDashboard;
