package com.vaapsi.ledger;

import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;

@Service
public class LedgerService {

    private static final String GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000";
    private final List<LedgerEntry> ledger = new CopyOnWriteArrayList<>();

    public synchronized LedgerEntry recordTransaction(String caseId, String action, double amount, String timestamp) {
        long newIndex = ledger.size() + 1;
        String prevHash = ledger.isEmpty() ? GENESIS_HASH : ledger.get(ledger.size() - 1).getCurrentHash();
        String ts = (timestamp != null && !timestamp.isBlank()) ? timestamp : Instant.now().toString();

        String currentHash = calculateHash(newIndex, caseId, action, amount, ts, prevHash);

        LedgerEntry entry = new LedgerEntry(newIndex, caseId, action, amount, ts, prevHash, currentHash);
        ledger.add(entry);
        return entry;
    }

    public Map<String, Object> verifyChain() {
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
                response.put("error", "Previous hash mismatch at index " + current.getIndex());
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
                response.put("error", "SHA-256 data hash mismatch at index " + current.getIndex() + ". Record content was modified!");
                return response;
            }
        }

        response.put("status", "TAMPER_PROOF_VERIFIED");
        response.put("total_records", ledger.size());
        response.put("integrity", "100%");
        response.put("latest_block_hash", ledger.get(ledger.size() - 1).getCurrentHash());
        return response;
    }

    public synchronized boolean tamperRecordForTesting(long index, String modifiedAction) {
        if (index <= 0 || index > ledger.size()) {
            return false;
        }
        LedgerEntry target = ledger.get((int) (index - 1));
        // Modify the action without re-signing the cryptographic hash!
        target.setAction(modifiedAction != null ? modifiedAction : "[TAMPERED_ACTION]");
        return true;
    }

    public List<LedgerEntry> getAllEntries() {
        return new ArrayList<>(ledger);
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
