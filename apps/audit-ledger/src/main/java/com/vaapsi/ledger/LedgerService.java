package com.vaapsi.ledger;

import org.springframework.stereotype.Service;

import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;

@Service
public class LedgerService {

    private static final String GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000";
    private static final String STORAGE_FILE = "target/ledger-chain.json";
    private final List<LedgerEntry> ledger = new CopyOnWriteArrayList<>();

    public LedgerService() {
        // Load existing ledger file from disk if present
        loadFromDisk();
    }

    public synchronized LedgerEntry recordTransaction(String caseId, String action, double amount, String timestamp) {
        long newIndex = ledger.size() + 1;
        String prevHash = ledger.isEmpty() ? GENESIS_HASH : ledger.get(ledger.size() - 1).getCurrentHash();
        String ts = (timestamp != null && !timestamp.isBlank()) ? timestamp : Instant.now().toString();

        String currentHash = calculateHash(newIndex, caseId, action, amount, ts, prevHash);

        LedgerEntry entry = new LedgerEntry(newIndex, caseId, action, amount, ts, prevHash, currentHash);
        ledger.add(entry);
        saveToDisk();
        return entry;
    }

    public Map<String, Object> verifyChain() {
        // Reload directly from raw disk file to catch external file edits
        loadFromDisk();

        Map<String, Object> response = new HashMap<>();

        if (ledger.isEmpty()) {
            response.put("status", "AWAITING_RUN");
            response.put("total_records", 0);
            response.put("message", "No audit records logged yet. Run a batch execution to populate the cryptographic chain.");
            return response;
        }

        for (int i = 0; i < ledger.size(); i++) {
            LedgerEntry current = ledger.get(i);
            String expectedPrevHash = (i == 0) ? GENESIS_HASH : ledger.get(i - 1).getCurrentHash();

            // 1. Verify link to previous hash
            if (!current.getPreviousHash().equals(expectedPrevHash)) {
                response.put("status", "TAMPERED");
                response.put("broken_at_record", current.getIndex());
                response.put("error", "Previous hash mismatch at index " + current.getIndex() + " (External file alteration detected)");
                return response;
            }

            // 2. Recompute SHA-256 hash for current block data
            String recomputedHash = calculateHash(
                    current.getIndex(),
                    current.getCaseId(),
                    current.getAction(),
                    current.getAmount(),
                    current.getTimestamp(),
                    current.getPreviousHash()
            );

            if (!current.getCurrentHash().equals(recomputedHash)) {
                response.put("status", "TAMPERED");
                response.put("broken_at_record", current.getIndex());
                response.put("error", "SHA-256 data hash mismatch at index " + current.getIndex() + ". Record content on disk was modified!");
                return response;
            }
        }

        response.put("status", "TAMPER_PROOF_VERIFIED");
        response.put("total_records", ledger.size());
        response.put("integrity", "100%");
        response.put("latest_block_hash", ledger.get(ledger.size() - 1).getCurrentHash());
        response.put("storage_source", STORAGE_FILE);
        return response;
    }

    public synchronized boolean tamperRecordForTesting(long index, String modifiedAction) {
        loadFromDisk();
        if (index <= 0 || index > ledger.size()) {
            return false;
        }
        LedgerEntry target = ledger.get((int) (index - 1));
        target.setAction(modifiedAction != null ? modifiedAction : "[TAMPERED_ACTION]");
        saveToDisk();
        return true;
    }

    public List<LedgerEntry> getAllEntries() {
        loadFromDisk();
        return new ArrayList<>(ledger);
    }

    private synchronized void saveToDisk() {
        try {
            File file = new File(STORAGE_FILE);
            file.getParentFile().mkdirs();
            try (FileWriter writer = new FileWriter(file, StandardCharsets.UTF_8)) {
                StringBuilder sb = new StringBuilder();
                sb.append("[\n");
                for (int i = 0; i < ledger.size(); i++) {
                    LedgerEntry e = ledger.get(i);
                    sb.append(String.format(
                            "  {\"index\":%d,\"caseId\":\"%s\",\"action\":\"%s\",\"amount\":%.2f,\"timestamp\":\"%s\",\"previousHash\":\"%s\",\"currentHash\":\"%s\"}%s\n",
                            e.getIndex(), escapeJson(e.getCaseId()), escapeJson(e.getAction()), e.getAmount(), escapeJson(e.getTimestamp()), escapeJson(e.getPreviousHash()), escapeJson(e.getCurrentHash()),
                            (i == ledger.size() - 1 ? "" : ",")
                    ));
                }
                sb.append("]");
                writer.write(sb.toString());
            }
        } catch (IOException e) {
            // Ignore write errors
        }
    }

    private synchronized void loadFromDisk() {
        File file = new File(STORAGE_FILE);
        if (!file.exists()) return;

        try (FileReader reader = new FileReader(file, StandardCharsets.UTF_8)) {
            char[] chars = new char[(int) file.length()];
            reader.read(chars);
            String json = new String(chars);

            ledger.clear();
            // Simple robust regex parser for LedgerEntry fields
            String[] objects = json.split("\\},\\s*\\{");
            for (String obj : objects) {
                Long idx = parseLong(obj, "index");
                String cId = parseString(obj, "caseId");
                String act = parseString(obj, "action");
                Double amt = parseDouble(obj, "amount");
                String ts = parseString(obj, "timestamp");
                String pHash = parseString(obj, "previousHash");
                String cHash = parseString(obj, "currentHash");

                if (idx != null && cId != null && cHash != null) {
                    ledger.add(new LedgerEntry(idx, cId, act, amt != null ? amt : 0.0, ts, pHash, cHash));
                }
            }
        } catch (Exception e) {
            // Fallback
        }
    }

    private String escapeJson(String input) {
        if (input == null) return "";
        return input.replace("\"", "\\\"");
    }

    private String parseString(String json, String key) {
        int keyIdx = json.indexOf("\"" + key + "\":\"");
        if (keyIdx == -1) return "";
        int start = keyIdx + key.length() + 4;
        int end = json.indexOf("\"", start);
        if (end == -1) return "";
        return json.substring(start, end);
    }

    private Long parseLong(String json, String key) {
        try {
            int keyIdx = json.indexOf("\"" + key + "\":");
            if (keyIdx == -1) return null;
            int start = keyIdx + key.length() + 3;
            int end = json.indexOf(",", start);
            if (end == -1) end = json.indexOf("}", start);
            if (end == -1) return null;
            return Long.parseLong(json.substring(start, end).trim());
        } catch (Exception e) {
            return null;
        }
    }

    private Double parseDouble(String json, String key) {
        try {
            int keyIdx = json.indexOf("\"" + key + "\":");
            if (keyIdx == -1) return null;
            int start = keyIdx + key.length() + 3;
            int end = json.indexOf(",", start);
            if (end == -1) end = json.indexOf("}", start);
            if (end == -1) return null;
            return Double.parseDouble(json.substring(start, end).trim());
        } catch (Exception e) {
            return null;
        }
    }

    public static String calculateHash(long index, String caseId, String action, double amount, String timestamp, String previousHash) {
        String dataToHash = index + ":" + caseId + ":" + action + ":" + amount + ":" + timestamp + ":" + previousHash;
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(dataToHash.getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 algorithm unavailable", e);
        }
    }
}
