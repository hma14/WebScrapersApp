import React, { useState, useEffect } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import SpinningLogo from "./Components/SpinningLogo";
import {
  Container,
  TextField,
  Button,
  Card,
  CardContent,
  Typography,
  Box,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Pagination,
  Paper,
  CircularProgress,
  IconButton,
} from "@mui/material";

import SendIcon from "@mui/icons-material/Send"; // arrow icon
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import dayjs from "dayjs";
import "./App.css";

const url = "http://localhost:9000";
//const url = "http://agent-back.lottotry.com:9000";

function App() {
  const [prompt, setPrompt] = useState("");
  const [results, setResults] = useState([]);
  const [isLoading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [error, setError] = useState(0);

  const submitPrompt = async () => {
    setLoading(true);
    const res = await axios.post(`${url}/api/query`, null, {
      params: { prompt },
    });
    setResults([res.data, ...results]);
    setLoading(false);
  };

  const pageSize = 5;

  useEffect(() => {
    const fetchResults = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`${url}/api/results`, {
          params: { page, page_size: pageSize }, // backend expects 1-based
        });
        setResults(res.data.results);
        setTotalPages(res.data.total_pages);
      } catch (err) {
        setError(err);
        setLoading(false);
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, [page, pageSize]);

  return (
    <Container maxWidth="md">
      {isLoading ? (
        <div className="loader-container">
          <CircularProgress size={100} />
        </div>
      ) : (
        ""
      )}
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
        }}
      >
        <SpinningLogo />
        <TextField
          fullWidth
          label="Ask anything"
          value={prompt}
          sx={{
            mt: 2,
            "& .MuiOutlinedInput-root": {
              borderRadius: "20px", // round the input box
            },
          }}
          onChange={(e) => setPrompt(e.target.value)}
        />

        <IconButton
          type="submit"
          sx={{
            ml: 1,
            bgcolor: "Highlight", // ChatGPT green
            color: "white",
            "&:hover": { bgcolor: "#0d8c6c" },
            display: "flex",
            justifyContent: "flex-end",
          }}
          onClick={submitPrompt}
          disabled={isLoading}
        >
          <SendIcon />
        </IconButton>
      </Box>
      {error ? (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography color="error">Error: {error}</Typography>
          </CardContent>
        </Card>
      ) : Array.isArray(results) && results.length > 0 ? (
        results.map((r) => (
          <Card key={r.id} sx={{ mt: 3 }}>
            <CardContent>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography sx={{ fontWeight: "bold", color: "Highlight" }}>
                    {r.prompt}
                    <Typography
                      variant="caption"
                      sx={{
                        ml: 2,
                        fontFamily: "-moz-initial",
                        color: "ActiveCaption",
                      }}
                    >
                      {dayjs(r.createdAt).format("MMM D, YYYY • h:mm A")}
                    </Typography>
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {r.results}
                  </ReactMarkdown>
                </AccordionDetails>
              </Accordion>
            </CardContent>
          </Card>
        ))
      ) : (
        <Typography sx={{ mt: 3 }}>No results yet.</Typography>
      )}
      <Pagination
        count={totalPages}
        page={page}
        onChange={(e, value) => setPage(value)}
        color="primary"
        sx={{ display: "flex", justifyContent: "center", mt: 2 }}
      />
    </Container>
  );
}

export default App;
