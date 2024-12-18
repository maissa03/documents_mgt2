import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import styled from "styled-components";
import api from "../api"; // Ensure this points to your API setup

// Styled Components
const DashboardContainer = styled.div`
  padding: 2rem;
  background-color: #f8f3ef;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const NavBar = styled.nav`
  background-color: #0474c4;
  color: white;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
`;

const Title = styled.h1`
  font-size: 2rem;
  margin: 0;
`;

const LogoutButton = styled.button`
  background-color: #ff4b5c;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;

  &:hover {
    background-color: #d13a4a;
  }
`;

const Section = styled.section`
  width: 90%;
  margin-top: 2rem;
  background-color: #fff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
`;

const Th = styled.th`
  text-align: center;
  padding: 1rem;
  background-color: #0474c4;
  color: white;
  font-weight: bold;
  border: 1px solid #ddd;
`;

const Td = styled.td`
  text-align: center;
  padding: 1rem;
  border: 1px solid #ddd;
`;

const Select = styled.select`
  padding: 0.5rem;
  font-size: 1rem;
  margin-right: 0.5rem;
  border-radius: 5px;
  border: 1px solid #ccc;
`;

const Button = styled.button`
  padding: 0.5rem 1rem;
  background-color: #0474c4;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;

  &:hover {
    background-color: #045bb5;
  }
`;

const Modal = styled.div`
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-width: 600px;
  width: 90%;

  /* Ensure text inside modal is not red */
  p, strong {
    color: #333; /* Set to neutral color (black/dark grey) */
    margin-bottom: 0.5rem;
  }
`;

const ModalTitle = styled.h3`
  color: #333; /* Ensure title text is dark */
  margin-bottom: 1rem;
`;


const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
`;

const CloseButton = styled.button`
  background-color: #ff4b5c;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;

  &:hover {
    background-color: #d13a4a;
  }
`;

const Message = styled.p`
  text-align: center;
  margin: 1rem 0;
  color: ${(props) => (props.success ? "green" : "red")};
  font-weight: bold;
`;

// Main Component
const ManagerDashboard = () => {
  const navigate = useNavigate();
  const [workflowInstances, setWorkflowInstances] = useState([]);
  const [selectedInstance, setSelectedInstance] = useState(null);
  const [selectedStatus, setSelectedStatus] = useState({});
  const [message, setMessage] = useState("");

  // Logout functionality
  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  // Fetch workflow instances
  const fetchWorkflowInstances = async () => {
    try {
      const response = await api.get("/documents/workflow-instances/", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
      setWorkflowInstances(response.data);
    } catch (err) {
      console.error("Error fetching workflow instances:", err);
    }
  };

  useEffect(() => {
    fetchWorkflowInstances();
  }, []);

  // Update status handler
  const handleStatusChange = (id, value) => {
    setSelectedStatus({ ...selectedStatus, [id]: value });
  };

  const updateStatus = async (id) => {
    const newStage = selectedStatus[id];
    if (!newStage) {
      setMessage("Please select a new stage.");
      return;
    }

    try {
      const response = await api.post(
        `/documents/workflow-instances/${id}/update-status/`,
        { current_stage: newStage },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );

      setMessage(response.data.message || "Stage updated successfully.");
      fetchWorkflowInstances();
    } catch (err) {
      console.error("Error updating stage:", err);
      setMessage("Failed to update stage.");
    }
  };

  const showDetails = (instance) => {
    setSelectedInstance(instance);
  };

  const closeModal = () => {
    setSelectedInstance(null);
  };

  const DOC_STAGES = [
    { value: "Approve Document", label: "Approve Document" },
    { value: "Review Document", label: "Review Document" },
    { value: "Request Changes", label: "Request Changes" },
  ];

  return (
    <DashboardContainer>
      <NavBar>
        <Title>Manager Dashboard</Title>
        <LogoutButton onClick={handleLogout}>Logout</LogoutButton>
      </NavBar>

      <Section>
        <h2 style={{ textAlign: "center", marginBottom: "1.5rem" }}>
          Workflow Instances
        </h2>
        {message && <Message>{message}</Message>}

        <Table>
          <thead>
            <tr>
              <Th>Document Title</Th>
              <Th>Current Stage</Th>
              <Th>Update Stage</Th>
              <Th>Details</Th>
            </tr>
          </thead>
          <tbody>
            {workflowInstances.length > 0 ? (
              workflowInstances.map((instance) => (
                <tr key={instance.id}>
                  <Td>{instance.document_title || "No Title"}</Td>
                  <Td>{instance.current_stage || "Not Set"}</Td>
                  <Td>
                    <Select
                      value={selectedStatus[instance.id] || instance.current_stage}
                      onChange={(e) =>
                        handleStatusChange(instance.id, e.target.value)
                      }
                    >
                      <option value="">-- Select Stage --</option>
                      {DOC_STAGES.map((stage) => (
                        <option key={stage.value} value={stage.value}>
                          {stage.label}
                        </option>
                      ))}
                    </Select>
                  </Td>
                  <Td>
                    <div style={{ display: "flex", justifyContent: "center", gap: "10px" }}>
                      <Button onClick={() => updateStatus(instance.id)}>Update</Button>
                      <Button onClick={() => showDetails(instance)}>View Details</Button>
                    </div>
                  </Td>

                </tr>
              ))
            ) : (
              <tr>
                <Td colSpan="4">No workflow instances available.</Td>
              </tr>
            )}
          </tbody>
        </Table>
      </Section>

      {selectedInstance && (
        <>
          <ModalOverlay onClick={closeModal} />
          <Modal>
            <ModalTitle>Document Details</ModalTitle>
            <p>
              <strong>Title:</strong> {selectedInstance.document_title}
            </p>
            <p>
              <strong>Content:</strong> {selectedInstance.document_content}
            </p>
            <p>
              <strong>Type:</strong> {selectedInstance.document_type}
            </p>
            <p>
              <strong>Status:</strong> {selectedInstance.document_status}
            </p>
            <CloseButton onClick={closeModal}>Close</CloseButton>
          </Modal>

        </>
      )}
    </DashboardContainer>
  );
};

export default ManagerDashboard;
