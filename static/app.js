// app.js - Frontend Client Logic for IVERI Terminal
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
    const viewText = document.getElementById("viewText");
    const btnToggleVoice = document.getElementById("btnToggleVoice");
    const voiceIcon = document.getElementById("voiceIcon");
    const voiceText = document.getElementById("voiceText");
    const btnThemeToggle = document.getElementById("btnThemeToggle");
    const themeIcon = document.getElementById("themeIcon");
    const themeText = document.getElementById("themeText");
    const voiceChoiceSelect = document.getElementById("voiceChoiceSelect");
    const ttsAudio = document.getElementById("ttsAudio");
    const audioStateTag = document.getElementById("audioStateTag");
    const audioCanvas = document.getElementById("audioVisualizer");
    const promptChips = document.querySelectorAll(".prompt-chip");

    // Application State
    let currentView = "terminal";
    let isVoiceEnabled = true;
    let isListening = false;
    let isProcessing = false;
    let recognition = null;
    let visualizerAnimationId = null;

    // VOICE ENGINE CHOICE ('new' vs 'classic')
    const savedVoice = localStorage.getItem("iveri_voice_choice") || "new";
    if (voiceChoiceSelect) {
        voiceChoiceSelect.value = savedVoice;
        voiceChoiceSelect.addEventListener("change", () => {
            localStorage.setItem("iveri_voice_choice", voiceChoiceSelect.value);
        });
    }

    // THEME MANAGEMENT (Light / Dark)
    const savedTheme = localStorage.getItem("iveri_theme") || "dark";
    setTheme(savedTheme);

    function setTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("iveri_theme", theme);
        if (theme === "dark") {
            themeIcon.textContent = "☀️";
            themeText.textContent = "Light";
        } else {
            themeIcon.textContent = "🌙";
            themeText.textContent = "Dark";
        }
    }

    btnThemeToggle.addEventListener("click", () => {
        const currentTheme = document.documentElement.getAttribute("data-theme") || "dark";
        const newTheme = currentTheme === "dark" ? "light" : "dark";
        setTheme(newTheme);
    });

    // AUDIO VISUALIZER
    const canvasCtx = audioCanvas.getContext("2d");
    function isDark() {
        return document.documentElement.getAttribute("data-theme") === "dark";
    }

    function drawIdleVisualizer() {
        canvasCtx.clearRect(0, 0, audioCanvas.width, audioCanvas.height);
        canvasCtx.fillStyle = isDark() ? "rgba(148, 163, 184, 0.25)" : "rgba(100, 116, 139, 0.25)";
        const barWidth = 3;
        const gap = 3;
        const totalBars = Math.floor(audioCanvas.width / (barWidth + gap));
        
        for (let i = 0; i < totalBars; i++) {
            const height = 2 + Math.sin(Date.now() / 400 + i * 0.2) * 1.5;
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
        const barWidth = 3;
        const gap = 3;
        const totalBars = Math.floor(audioCanvas.width / (barWidth + gap));

        for (let i = 0; i < totalBars; i++) {
            let height = 3;
            if (isListening) {
                height = 4 + Math.random() * 16;
                canvasCtx.fillStyle = "#e11d48"; // Rose
            } else if (isProcessing) {
                height = 3 + Math.sin(Date.now() / 150 + i * 0.4) * 8;
                canvasCtx.fillStyle = "#d97706"; // Amber
            } else if (!ttsAudio.paused) {
                height = 4 + Math.random() * 18;
                canvasCtx.fillStyle = "#059669"; // Emerald
            }
            canvasCtx.fillRect(i * (barWidth + gap), (audioCanvas.height - height) / 2, barWidth, height);
        }
        visualizerAnimationId = requestAnimationFrame(drawActiveVisualizer);
    }

    // Toggle View (Terminal vs Chat)
    btnToggleView.addEventListener("click", () => {
        if (currentView === "terminal") {
            currentView = "chat";
            terminalViewport.classList.remove("active");
            chatViewport.classList.add("active");
            viewText.textContent = "Chat View";
            chatViewport.scrollTop = chatViewport.scrollHeight;
        } else {
            currentView = "terminal";
            chatViewport.classList.remove("active");
            terminalViewport.classList.add("active");
            viewText.textContent = "Terminal";
            terminalViewport.scrollTop = terminalViewport.scrollHeight;
        }
    });

    // Toggle Voice Output
    btnToggleVoice.addEventListener("click", () => {
        isVoiceEnabled = !isVoiceEnabled;
        if (isVoiceEnabled) {
            btnToggleVoice.classList.add("active");
            voiceIcon.textContent = "🔊";
            voiceText.textContent = "Voice On";
        } else {
            btnToggleVoice.classList.remove("active");
            voiceIcon.textContent = "🔇";
            voiceText.textContent = "Voice Off";
            if (!ttsAudio.paused) ttsAudio.pause();
            if (window.speechSynthesis) window.speechSynthesis.cancel();
        }
    });

    // Dual-Engine Speech-to-Text: Browser SpeechRecognition + Direct WebAudio Fallback
    let silenceTimer = null;
    let currentSpeechText = "";
    let isDirectRecording = false;
    let directMediaStream = null;
    let directAudioContext = null;
    let directAudioProcessor = null;
    let directPcmBuffers = [];
    let webSpeechNetworkBlocked = false;

    function createRecognizer() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return null;

        const rec = new SpeechRecognition();
        rec.continuous = false; // Set false to prevent extension loop on network error
        rec.interimResults = true;
        rec.lang = "en-US";
        rec.maxAlternatives = 1;

        rec.onstart = () => {
            isListening = true;
            btnMic.classList.add("listening");
            audioStateTag.textContent = "Listening...";
            cliInput.placeholder = "Listening... Speak now (tap mic to stop)";
            cancelAnimationFrame(visualizerAnimationId);
            drawActiveVisualizer();
        };

        rec.onresult = (event) => {
            let interim = "";
            let final = "";
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const text = event.results[i][0].transcript;
                if (event.results[i].isFinal) final += text;
                else interim += text;
            }
            const spoken = (final || interim).trim();
            if (spoken) {
                cliInput.value = spoken;
                currentSpeechText = spoken;
                clearTimeout(silenceTimer);
                silenceTimer = setTimeout(() => {
                    if (isListening && currentSpeechText) {
                        const finalQuery = currentSpeechText;
                        stopListening();
                        handleSubmit(finalQuery);
                    }
                }, 1800);
            }
        };

        rec.onerror = (event) => {
            console.warn("Speech recognition notice:", event.error);
            if (event.error === "no-speech") return;
            
            // If browser extension / adblocker blocks Google speech API, switch immediately to Direct Mic
            if (event.error === "network") {
                webSpeechNetworkBlocked = true;
                stopListening();
                console.log("Switching to Direct Local Audio Recording...");
                startDirectAudioRecording();
                return;
            }

            if (event.error === "not-allowed" || event.error === "service-not-allowed") {
                stopListening();
                alert("Microphone permission was denied. Please allow microphone access in your browser address bar.");
            }
        };

        rec.onend = () => {
            if (isListening && !webSpeechNetworkBlocked) {
                stopListening();
                if (currentSpeechText) {
                    handleSubmit(currentSpeechText);
                }
            }
        };

        return rec;
    }

    // Direct Audio Recording via Web Audio API (Bypasses Google Speech Servers completely)
    async function startDirectAudioRecording() {
        try {
            isDirectRecording = true;
            isListening = true;
            directPcmBuffers = [];

            directMediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            directAudioContext = new (window.AudioContext || window.webkitAudioContext)();
            const source = directAudioContext.createMediaStreamSource(directMediaStream);
            
            directAudioProcessor = directAudioContext.createScriptProcessor(4096, 1, 1);
            source.connect(directAudioProcessor);
            directAudioProcessor.connect(directAudioContext.destination);

            directAudioProcessor.onaudioprocess = (e) => {
                if (!isDirectRecording) return;
                const input = e.inputBuffer.getChannelData(0);
                directPcmBuffers.push(new Float32Array(input));
            };

            btnMic.classList.add("listening");
            audioStateTag.textContent = "Listening (Direct Mic)... Tap to send";
            cliInput.placeholder = "Listening directly via microphone... Tap mic when done";
            cancelAnimationFrame(visualizerAnimationId);
            drawActiveVisualizer();
        } catch (err) {
            console.error("Direct audio recording failed:", err);
            stopDirectAudioRecording();
            alert("Microphone access error: " + err.message);
        }
    }

    async function stopDirectAudioRecording() {
        isDirectRecording = false;
        isListening = false;
        btnMic.classList.remove("listening");
        audioStateTag.textContent = "Processing speech...";
        cliInput.placeholder = "Transcribing audio...";

        if (directAudioProcessor) {
            try { directAudioProcessor.disconnect(); } catch (e) {}
        }
        if (directAudioContext) {
            try { directAudioContext.close(); } catch (e) {}
        }
        if (directMediaStream) {
            try { directMediaStream.getTracks().forEach(t => t.stop()); } catch (e) {}
        }

        cancelAnimationFrame(visualizerAnimationId);
        drawIdleVisualizer();

        if (directPcmBuffers.length === 0) {
            audioStateTag.textContent = "Ready";
            cliInput.placeholder = "Ask a question, enter math, or run a command... (Enter)";
            return;
        }

        // Resample/encode to 16kHz mono WAV
        const sampleRate = directAudioContext ? directAudioContext.sampleRate : 44100;
        let totalLen = directPcmBuffers.reduce((a, b) => a + b.length, 0);
        let merged = new Float32Array(totalLen);
        let off = 0;
        for (let b of directPcmBuffers) {
            merged.set(b, off);
            off += b.length;
        }
        directPcmBuffers = [];

        // Downsample to 16kHz if needed
        const downsampled = downsampleBuffer(merged, sampleRate, 16000);
        const wavBlob = encodeWAVBlob(downsampled, 16000);

        try {
            const resp = await fetch("/api/transcribe", {
                method: "POST",
                headers: { "Content-Type": "audio/wav" },
                body: wavBlob
            });
            const resData = await resp.json();
            const text = (resData.transcript || "").trim();
            audioStateTag.textContent = "Ready";
            cliInput.placeholder = "Ask a question, enter math, or run a command... (Enter)";
            if (text) {
                cliInput.value = text;
                handleSubmit(text);
            }
        } catch (e) {
            console.warn("Direct transcription network error:", e);
            audioStateTag.textContent = "Ready";
            cliInput.placeholder = "Ask a question, enter math, or run a command... (Enter)";
        }
    }

    function downsampleBuffer(buffer, inputSampleRate, outputSampleRate) {
        if (inputSampleRate === outputSampleRate) return buffer;
        const ratio = inputSampleRate / outputSampleRate;
        const newLen = Math.round(buffer.length / ratio);
        const result = new Float32Array(newLen);
        for (let i = 0; i < newLen; i++) {
            result[i] = buffer[Math.floor(i * ratio)];
        }
        return result;
    }

    function encodeWAVBlob(samples, sampleRate) {
        const buffer = new ArrayBuffer(44 + samples.length * 2);
        const view = new DataView(buffer);
        const writeString = (v, offset, s) => {
            for (let i = 0; i < s.length; i++) v.setUint8(offset + i, s.charCodeAt(i));
        };

        writeString(view, 0, 'RIFF');
        view.setUint32(4, 36 + samples.length * 2, true);
        writeString(view, 8, 'WAVE');
        writeString(view, 12, 'fmt ');
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true); // PCM
        view.setUint16(22, 1, true); // Mono
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, sampleRate * 2, true);
        view.setUint16(32, 2, true);
        view.setUint16(34, 16, true);
        writeString(view, 36, 'data');
        view.setUint32(40, samples.length * 2, true);

        let idx = 44;
        for (let i = 0; i < samples.length; i++) {
            let s = Math.max(-1, Math.min(1, samples[i]));
            view.setInt16(idx, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
            idx += 2;
        }
        return new Blob([view], { type: 'audio/wav' });
    }

    recognition = createRecognizer();

    function stopListening() {
        isListening = false;
        clearTimeout(silenceTimer);
        btnMic.classList.remove("listening");
        audioStateTag.textContent = "Ready";
        cliInput.placeholder = "Ask a question, enter math, or run a command... (Enter)";
        if (recognition) {
            try { recognition.stop(); } catch (e) {}
        }
        cancelAnimationFrame(visualizerAnimationId);
        drawIdleVisualizer();
    }

    btnMic.addEventListener("click", async () => {
        if (isDirectRecording) {
            stopDirectAudioRecording();
            return;
        }

        if (isListening) {
            clearTimeout(silenceTimer);
            const textToSubmit = currentSpeechText || cliInput.value.trim();
            stopListening();
            if (textToSubmit) {
                handleSubmit(textToSubmit);
            }
            return;
        }

        // If Web Speech API was blocked by an extension, use Direct Mic immediately
        if (webSpeechNetworkBlocked) {
            startDirectAudioRecording();
            return;
        }

        // Request browser microphone permission
        try {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                stream.getTracks().forEach(track => track.stop());
            }
        } catch (e) {}

        currentSpeechText = "";
        cliInput.value = "";

        if (!recognition) {
            recognition = createRecognizer();
        }

        if (recognition) {
            try {
                isListening = true;
                recognition.start();
            } catch (e) {
                console.warn("Speech start fallback:", e);
                startDirectAudioRecording();
            }
        } else {
            startDirectAudioRecording();
        }
    });

    // Quick Prompt Chips
    promptChips.forEach(chip => {
        chip.addEventListener("click", () => {
            const query = chip.getAttribute("data-query");
            if (query && !isProcessing) {
                cliInput.value = query;
                handleSubmit(query);
            }
        });
    });

    // Form Submit
    consoleForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const text = cliInput.value.trim();
        if (text && !isProcessing) {
            handleSubmit(text);
        }
    });

    // Core Submit & API Communication
    async function handleSubmit(text) {
        if (!text || isProcessing) return;
        isProcessing = true;
        cliInput.value = "";
        cliInput.disabled = true;
        btnSend.disabled = true;
        audioStateTag.textContent = "Thinking...";
        cancelAnimationFrame(visualizerAnimationId);
        drawActiveVisualizer();

        // Render User Input
        appendUserMessage(text);

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: text,
                    use_history: true,
                    voice_response: isVoiceEnabled,
                    voice_choice: voiceChoiceSelect ? voiceChoiceSelect.value : "new"
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            const reply = data.response || "No response received.";
            const source = data.source || "ai";

            appendAssistantMessage(reply, source);

            // AUTO-OPEN WEBSITE / SEARCH IN BROWSER
            if (data.open_url) {
                console.log("Opening URL in browser:", data.open_url);
                try {
                    window.open(data.open_url, "_blank");
                } catch (e) {
                    console.warn("Popup blocked:", e);
                }
            }

            if (isVoiceEnabled) {
                playAudioResponse(reply, data.audio_url);
            } else {
                finishProcessing();
            }

        } catch (err) {
            appendAssistantMessage(`Error connecting to assistant: ${err.message}`, "command");
            finishProcessing();
        }
    }

    function finishProcessing() {
        isProcessing = false;
        cliInput.disabled = false;
        btnSend.disabled = false;
        cliInput.focus();
        audioStateTag.textContent = "Ready";
        cancelAnimationFrame(visualizerAnimationId);
        drawIdleVisualizer();
    }

    // Audio Playback with Choice between New and Classic Voice
    function playAudioResponse(text, audioUrl) {
        audioStateTag.textContent = "Speaking...";
        cancelAnimationFrame(visualizerAnimationId);
        drawActiveVisualizer();

        const currentChoice = voiceChoiceSelect ? voiceChoiceSelect.value : "new";

        // If user chose classic voice, speak directly using native system voice
        if (currentChoice === "classic" || !audioUrl) {
            fallbackBrowserTTS(text);
            return;
        }

        // User chose new voice (ElevenLabs Flash v2.5)
        ttsAudio.src = audioUrl;
        ttsAudio.play().then(() => {
            ttsAudio.onended = () => finishProcessing();
        }).catch(() => fallbackBrowserTTS(text));
    }

    function fallbackBrowserTTS(text) {
        if ("speechSynthesis" in window) {
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.05;
            utterance.onend = () => finishProcessing();
            utterance.onerror = () => finishProcessing();
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
        const tagLabel = source === "rag" ? "Online RAG" : (source === "command" ? "Local" : "Gemini");

        entry.innerHTML = `
            <div class="term-prompt-line">iveri&gt; ${escapeHtml(userText)}</div>
            <div class="term-response-line">
                <span class="term-tag ${tagClass}">[${tagLabel}]</span>${escapeHtml(responseText)}
            </div>
        `;
        terminalFeed.appendChild(entry);
        terminalViewport.scrollTop = terminalViewport.scrollHeight;
    }

    // Append to Chat View
    function appendChatBubble(text, sender, source = "default") {
        const bubble = document.createElement("div");
        bubble.className = `chat-message ${sender}`;

        const tagClass = source === "rag" ? "rag" : (source === "command" ? "command" : "ai");
        const tagLabel = source === "rag" ? "Online RAG" : (source === "command" ? "Local" : "Gemini Flash");

        if (sender === "user") {
            bubble.innerHTML = `<div class="message-text">${escapeHtml(text)}</div>`;
        } else {
            bubble.innerHTML = `
                <div class="message-meta">
                    <span class="sender-name">IVERI</span>
                    <span class="source-pill ${tagClass}">${tagLabel}</span>
                </div>
                <div class="message-text">${escapeHtml(text)}</div>
            `;
        }
        chatFeed.appendChild(bubble);
        chatViewport.scrollTop = chatViewport.scrollHeight;
    }

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
});
