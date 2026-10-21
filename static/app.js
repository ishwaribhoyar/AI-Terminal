// app.js - Frontend Client Logic for IVERI AI Terminal
document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const terminalViewport = document.getElementById("terminalViewport");
    const chatViewport = document.getElementById("chatViewport");
    const terminalFeed = document.getElementById("terminalFeed");
    const chatFeed = document.getElementById("chatFeed");
    const consoleForm = document.getElementById("consoleForm");
    const cliInput = document.getElementById("cliInput");
    const btnSend = document.getElementById("btnSend");
    const btnMic = document.getElementById("btnMic");
    const btnToggleView = document.getElementById("btnToggleView");
    const btnToggleVoice = document.getElementById("btnToggleVoice");
    const voiceIcon = document.getElementById("voiceIcon");
    const voiceText = document.getElementById("voiceText");
    const ttsAudio = document.getElementById("ttsAudio");
    const audioStateTag = document.getElementById("audioStateTag");
    const audioCanvas = document.getElementById("audioVisualizer");
    const quickChips = document.querySelectorAll(".chip");

    // Application State
    let currentView = "terminal"; // 'terminal' | 'chat'
    let isVoiceEnabled = true;
    let isListening = false;
    let isProcessing = false;
    let recognition = null;
    let audioContext = null;
    let analyser = null;
    let visualizerAnimationId = null;

    // Initialize Web Audio Visualizer
    const canvasCtx = audioCanvas.getContext("2d");
    function drawIdleVisualizer() {
        canvasCtx.clearRect(0, 0, audioCanvas.width, audioCanvas.height);
        canvasCtx.fillStyle = "rgba(0, 240, 255, 0.2)";
        const barWidth = 3;
        const gap = 3;
        const totalBars = Math.floor(audioCanvas.width / (barWidth + gap));
        
        for (let i = 0; i < totalBars; i++) {
            const height = 2 + Math.sin(Date.now() / 300 + i * 0.2) * 1.5;
            canvasCtx.fillRect(i * (barWidth + gap), (audioCanvas.height - height) / 2, barWidth, height);
        }
        visualizerAnimationId = requestAnimationFrame(drawIdleVisualizer);
    }
    drawIdleVisualizer();

    function drawActiveVisualizer() {
        if (!isProcessing && !isListening && ttsAudio.paused) {
            drawIdleVisualizer();
            return;
        }
        canvasCtx.clearRect(0, 0, audioCanvas.width, audioCanvas.height);
        const barWidth = 4;
        const gap = 2;
        const totalBars = Math.floor(audioCanvas.width / (barWidth + gap));

        for (let i = 0; i < totalBars; i++) {
            let height = 4;
            if (isListening) {
                height = 6 + Math.random() * 16;
                canvasCtx.fillStyle = "#ff3366";
            } else if (isProcessing) {
                height = 4 + Math.sin(Date.now() / 150 + i * 0.4) * 8;
                canvasCtx.fillStyle = "#ff9900";
            } else if (!ttsAudio.paused) {
                height = 6 + Math.random() * 22;
                canvasCtx.fillStyle = "#00ff9d";
            }
            canvasCtx.fillRect(i * (barWidth + gap), (audioCanvas.height - height) / 2, barWidth, height);
        }
        visualizerAnimationId = requestAnimationFrame(drawActiveVisualizer);
    }

    // Toggle View (Terminal Shell vs Neural Chat)
    btnToggleView.addEventListener("click", () => {
        if (currentView === "terminal") {
            currentView = "chat";
            terminalViewport.classList.remove("active");
            chatViewport.classList.add("active");
            btnToggleView.querySelector(".icon").textContent = "💬";
            btnToggleView.querySelector(".btn-text").textContent = "CHAT VIEW";
            chatViewport.scrollTop = chatViewport.scrollHeight;
        } else {
            currentView = "terminal";
            chatViewport.classList.remove("active");
            terminalViewport.classList.add("active");
            btnToggleView.querySelector(".icon").textContent = "💻";
            btnToggleView.querySelector(".btn-text").textContent = "TERMINAL";
            terminalViewport.scrollTop = terminalViewport.scrollHeight;
        }
    });

    // Toggle Voice Output
    btnToggleVoice.addEventListener("click", () => {
        isVoiceEnabled = !isVoiceEnabled;
        if (isVoiceEnabled) {
            btnToggleVoice.classList.add("active");
            voiceIcon.textContent = "🔊";
            voiceText.textContent = "VOICE ON";
        } else {
            btnToggleVoice.classList.remove("active");
            voiceIcon.textContent = "🔇";
            voiceText.textContent = "VOICE OFF";
            if (!ttsAudio.paused) {
                ttsAudio.pause();
            }
            if (window.speechSynthesis) {
                window.speechSynthesis.cancel();
            }
        }
    });

    // Web Speech API Initialization (Browser-native STT)
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";

        recognition.onstart = () => {
            isListening = true;
            btnMic.classList.add("listening");
            audioStateTag.textContent = "LISTENING...";
            audioStateTag.style.color = "#ff3366";
            cancelAnimationFrame(visualizerAnimationId);
            drawActiveVisualizer();
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            cliInput.value = transcript;
            handleSubmit(transcript);
        };

        recognition.onerror = (event) => {
            console.warn("Speech recognition error:", event.error);
            stopListening();
        };

        recognition.onend = () => {
            stopListening();
        };
    } else {
        btnMic.title = "Voice recognition not supported in this browser";
        btnMic.style.opacity = "0.5";
    }

    function stopListening() {
        isListening = false;
        btnMic.classList.remove("listening");
        audioStateTag.textContent = "IDLE";
        audioStateTag.style.color = "#00f0ff";
        cancelAnimationFrame(visualizerAnimationId);
        drawIdleVisualizer();
    }

    btnMic.addEventListener("click", () => {
        if (!recognition) {
            appendTerminalMessage("System", "Web Speech API is not supported in this browser. Please type.", "info");
            return;
        }
        if (isListening) {
            recognition.stop();
        } else {
            try {
                recognition.start();
            } catch (e) {
                console.error(e);
            }
        }
    });

    // Quick Action Chips
    quickChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const query = chip.getAttribute("data-query");
            if (query && !isProcessing) {
                cliInput.value = query;
                handleSubmit(query);
            }
        });
    });

    // Form Submit Handler
    consoleForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = cliInput.value.trim();
        if (text && !isProcessing) {
            handleSubmit(text);
        }
    });

    // Core Send & API Request Handler
    async function handleSubmit(text) {
        if (!text || isProcessing) return;
        isProcessing = true;
        cliInput.value = "";
        cliInput.disabled = true;
        btnSend.disabled = true;
        audioStateTag.textContent = "PROCESSING...";
        audioStateTag.style.color = "#ff9900";
        cancelAnimationFrame(visualizerAnimationId);
        drawActiveVisualizer();

        // Append User Input to Views
        appendUserMessage(text);

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: text,
                    use_history: true,
                    voice_response: isVoiceEnabled
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: Failed to reach IVERI`);
            }

            const data = await response.json();
            const reply = data.response || "No response received.";
            const source = data.source || "ai";

            // Append response to Views
            appendAssistantMessage(reply, source);

            // Handle Audio Playback
            if (isVoiceEnabled) {
                playAudioResponse(reply, data.audio_url);
            } else {
                finishProcessing();
            }

        } catch (err) {
            console.error("Communication error:", err);
            appendAssistantMessage(`Error connecting to IVERI engine: ${err.message}`, "command");
            finishProcessing();
        }
    }

    function finishProcessing() {
        isProcessing = false;
        cliInput.disabled = false;
        btnSend.disabled = false;
        cliInput.focus();
        audioStateTag.textContent = "IDLE";
        audioStateTag.style.color = "#00f0ff";
        cancelAnimationFrame(visualizerAnimationId);
        drawIdleVisualizer();
    }

    // Audio Playback: ElevenLabs Stream -> Fallback to Web Speech Synthesis
    function playAudioResponse(text, audioUrl) {
        audioStateTag.textContent = "SPEAKING...";
        audioStateTag.style.color = "#00ff9d";
        cancelAnimationFrame(visualizerAnimationId);
        drawActiveVisualizer();

        if (audioUrl) {
            ttsAudio.src = audioUrl;
            ttsAudio.play().then(() => {
                ttsAudio.onended = () => {
                    finishProcessing();
                };
            }).catch(err => {
                console.warn("ElevenLabs audio play rejected, using browser voice fallback:", err);
                fallbackBrowserTTS(text);
            });
        } else {
            fallbackBrowserTTS(text);
        }
    }

    function fallbackBrowserTTS(text) {
        if ("speechSynthesis" in window) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.05;
            utterance.pitch = 1.0;
            utterance.onend = () => {
                finishProcessing();
            };
            utterance.onerror = () => {
                finishProcessing();
            };
            window.speechSynthesis.speak(utterance);
        } else {
            finishProcessing();
        }
    }

    // Append to Terminal View
    function appendTerminalEntry(userText, responseText, source) {
        const entry = document.createElement("div");
        entry.className = "term-entry";

        const tagClass = source === "rag" ? "rag" : (source === "command" ? "command" : "ai");
        const tagLabel = source === "rag" ? "ONLINE RAG" : (source === "command" ? "LOCAL" : "GEMINI");

        entry.innerHTML = `
            <div class="term-prompt-line">iveri@ai:~$ ${escapeHtml(userText)}</div>
            <div class="term-response-line">
                <span class="term-tag ${tagClass}">[${tagLabel}]</span>${escapeHtml(responseText)}
            </div>
        `;
        terminalFeed.appendChild(entry);
        terminalViewport.scrollTop = terminalViewport.scrollHeight;
    }

    function appendTerminalMessage(prefix, msg, level = "info") {
        const log = document.createElement("div");
        log.className = `term-log ${level}`;
        log.innerHTML = `<span class="log-prefix">[${escapeHtml(prefix)}]</span> ${escapeHtml(msg)}`;
        terminalFeed.appendChild(log);
        terminalViewport.scrollTop = terminalViewport.scrollHeight;
    }

    // Append to Chat View
    function appendChatBubble(text, sender, source = "default") {
        const bubble = document.createElement("div");
        bubble.className = `chat-bubble ${sender}`;

        const tagClass = source === "rag" ? "rag" : (source === "command" ? "command" : "ai");
        const tagLabel = source === "rag" ? "ONLINE RAG" : (source === "command" ? "LOCAL" : "GEMINI FLASH");

        if (sender === "user") {
            bubble.innerHTML = `
                <div class="bubble-header">
                    <span class="author-badge">OPERATOR</span>
                </div>
                <div class="bubble-content">${escapeHtml(text)}</div>
            `;
        } else {
            bubble.innerHTML = `
                <div class="bubble-header">
                    <span class="author-badge">IVERI AI</span>
                    <span class="source-tag ${tagClass}">${tagLabel}</span>
                </div>
                <div class="bubble-content">${escapeHtml(text)}</div>
            `;
        }
        chatFeed.appendChild(bubble);
        chatViewport.scrollTop = chatViewport.scrollHeight;
    }

    // Unified Messengers
    let pendingUserText = "";
    function appendUserMessage(text) {
        pendingUserText = text;
        appendChatBubble(text, "user");
    }

    function appendAssistantMessage(text, source) {
        appendTerminalEntry(pendingUserText, text, source);
        appendChatBubble(text, "assistant", source);
    }

    function escapeHtml(str) {
        return (str || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Poll System Status
    fetch("/api/status")
        .then(r => r.json())
        .then(data => {
            console.log("IVERI Status:", data);
        })
        .catch(err => console.warn("Status check note:", err));
});
