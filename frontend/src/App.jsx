
import { useState } from "react";
import "./App.css";
import axios from "axios";

function App() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [organizationCode, setOrganizationCode] = useState("");

  const [exceptions, setExceptions] = useState([]);
  const [locations, setLocations] = useState([]);

  const [reasonCode, setReasonCode] = useState("");
  const [locationId, setLocationId] = useState("");

  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  // Q&A states
const [question, setQuestion] = useState("");
const [qaResult, setQaResult] = useState(null);
const [qaLoading, setQaLoading] = useState(false);
const [qaError, setQaError] = useState("");

  // Summary calculations
  const totalExceptions = exceptions.length;

  const valueMismatches = exceptions.filter(
    (item) => item.reason_code === "VALUE_MISMATCH"
  ).length;

  const duplicateEntries = exceptions.filter(
    (item) => item.reason_code === "DUPLICATE_ENTRY"
  ).length;

  const missingRecords = exceptions.filter(
    (item) =>
      item.reason_code === "MISSING_IN_SYSTEM_B" ||
      item.reason_code === "UNMATCHED_IN_SYSTEM_A"
  ).length;

  // Ask a question about reconciliation data
const handleAskQuestion = async () => {
  if (!question.trim()) {
    return;
  }

  setQaLoading(true);
  setQaError("");
  setQaResult(null);

  try {
    const response = await axios.post(
      "http://localhost:8000/qa/ask",
      {
        question: question,
      },
      {
        withCredentials: true,
      }
    );

    setQaResult(response.data);
  } catch (error) {
    console.error("Q&A failed:", error);

    setQaError(
      error.response?.data?.detail ||
      "Unable to process your question."
    );
  } finally {
    setQaLoading(false);
  }
};

  // Login
  const handleLogin = async (event) => {
    event.preventDefault();
    setErrorMessage("");

    try {
      // Step 1: Authenticate user
      await axios.post(
        "http://localhost:8000/auth/login",
        {
          email,
          password,
          organization_code: organizationCode,
        },
        {
          withCredentials: true,
        }
      );

      // Step 2: Fetch exceptions
      const exceptionsResponse = await axios.get(
        "http://localhost:8000/exceptions/",
        {
          withCredentials: true,
        }
      );

      // Step 3: Fetch organization locations
      const locationsResponse = await axios.get(
        "http://localhost:8000/locations/",
        {
          withCredentials: true,
        }
      );

      // Step 4: Update frontend state
      setExceptions(exceptionsResponse.data);
      setLocations(locationsResponse.data);
      setIsLoggedIn(true);

      console.log("Login successful");
    } catch (error) {
      console.error(
        "Login failed:",
        error.response?.data || error.message
      );

      setErrorMessage(
        error.response?.data?.detail ||
        "Login failed. Please check your details or backend API."
      );
    }
  };


const handleLogout = async () => {
  try {
    await axios.post(
      "http://localhost:8000/auth/logout",
      {},
      {
        withCredentials: true,
      }
    );

    // Clear frontend data
    setExceptions([]);
    setLocations([]);
    setReasonCode("");
    setLocationId("");
    setIsLoggedIn(false);

    setPassword("");
    setErrorMessage("");

    console.log("Logout successful");
  } catch (error) {
    console.error(
      "Logout failed:",
      error.response?.data || error.message
    );
  }
};


  // Apply filters
  const handleFilter = async () => {
    try {
      const response = await axios.get(
        "http://localhost:8000/exceptions/",
        {
          params: {
            reason_code: reasonCode || undefined,
            location_id: locationId || undefined,
          },
          withCredentials: true,
        }
      );

      setExceptions(response.data);
    } catch (error) {
      console.error(
        "Filter failed:",
        error.response?.data || error.message
      );
    }
  };

  return (
    <div className="login-container">

      {!isLoggedIn ? (
        <div className="login-card">
          <h1>DealerOS</h1>
          <p>Dealer Reconciliation Platform</p>

          <form onSubmit={handleLogin}>
            <label>Email</label>
            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />

            <label>Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />

            <label>Organization Code</label>
            <input
              type="text"
              placeholder="Example: ORG-A"
              value={organizationCode}
              onChange={(event) =>
                setOrganizationCode(event.target.value)
              }
              required
            />

            {errorMessage && (
              <p style={{ color: "red" }}>
                {errorMessage}
              </p>
            )}

            <button type="submit">
              Login
            </button>
          </form>
        </div>
      ) : (
        <div className="exceptions-container">
          <h1>DealerOS Dashboard</h1>
<button className="logout-button" onClick={handleLogout}>
  Logout
</button>
          <h2>Reconciliation Exceptions</h2>
          {/* Natural Language Q&A */}
<div className="qa-section">
  <h2>Ask DealerOS</h2>

  <p>
    Ask questions about your organization's reconciliation data.
  </p>

  <div className="qa-input">
    <input
      type="text"
      placeholder="Example: How many value mismatches are there?"
      value={question}
      onChange={(event) => setQuestion(event.target.value)}
    />

    <button
      onClick={handleAskQuestion}
      disabled={qaLoading || !question.trim()}
    >
      {qaLoading ? "Thinking..." : "Ask"}
    </button>
  </div>

  {qaError && (
    <p style={{ color: "red" }}>{qaError}</p>
  )}

  {qaResult && (
    <div className="qa-result">
      <h3>Answer</h3>

      <p>{qaResult.answer}</p>

      <p>
        <strong>Grounded:</strong>{" "}
        {qaResult.grounded ? "Yes" : "No"}
      </p>

      {qaResult.citations.length > 0 && (
        <>
          <h4>Source Citations</h4>

          <ul>
            {qaResult.citations.map((citation) => (
              <li key={citation.exception_id}>
                Exception #{citation.exception_id} —{" "}
                {citation.normalized_reference} (
                {citation.reason_code})
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  )}
</div>

          {/* Summary Cards */}
          <div className="summary-cards">
            <div className="summary-card">
              <h3>Total Exceptions</h3>
              <h2>{totalExceptions}</h2>
            </div>

            <div className="summary-card">
              <h3>Value Mismatches</h3>
              <h2>{valueMismatches}</h2>
            </div>

            <div className="summary-card">
              <h3>Duplicate Entries</h3>
              <h2>{duplicateEntries}</h2>
            </div>

            <div className="summary-card">
              <h3>Missing / Unmatched</h3>
              <h2>{missingRecords}</h2>
            </div>
          </div>

          {/* Filters */}
          <div className="filters">
            <select
              value={reasonCode}
              onChange={(event) =>
                setReasonCode(event.target.value)
              }
            >
              <option value="">All Reason Codes</option>
              <option value="MISSING_IN_SYSTEM_B">
                Missing in System B
              </option>
              <option value="UNMATCHED_IN_SYSTEM_A">
                Unmatched in System A
              </option>
              <option value="DUPLICATE_ENTRY">
                Duplicate Entry
              </option>
              <option value="VALUE_MISMATCH">
                Value Mismatch
              </option>
              <option value="DATE_MISMATCH">
                Date Mismatch
              </option>
              <option value="LOCATION_MISMATCH">
                Location Mismatch
              </option>
              <option value="INVALID_AMOUNT">
                Invalid Amount
              </option>
            </select>

            {/* Dynamic Locations */}
            <select
              value={locationId}
              onChange={(event) =>
                setLocationId(event.target.value)
              }
            >
              <option value="">All Locations</option>

              {locations.map((location) => (
                <option
                  key={location.id}
                  value={location.id}
                >
                  {location.location_code} - {location.name}
                </option>
              ))}
            </select>

            <button onClick={handleFilter}>
              Apply Filters
            </button>
          </div>

          <p>Total Exceptions: {exceptions.length}</p>

          {/* Exceptions Table */}
          <table>
            <thead>
              <tr>
                <th>Reference</th>
                <th>Reason</th>
                <th>Location</th>
                <th>Description</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {exceptions.map((item) => (
                <tr key={item.id}>
                  <td>{item.normalized_reference}</td>
                  <td>{item.reason_code}</td>
                  <td>{item.location_id}</td>
                  <td>{item.description}</td>
                  <td>{item.status}</td>
                </tr>
              ))}

              {exceptions.length === 0 && (
                <tr>
                  <td colSpan="5">
                    No exceptions found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

    </div>
  );
}

export default App;
