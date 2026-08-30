package com.vaapsi.ledger;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/ledger")
@CrossOrigin(origins = "*")
public class LedgerController {

    private final LedgerService ledgerService;

    public LedgerController(LedgerService ledgerService) {
        this.ledgerService = ledgerService;
    }

    @PostMapping("/record")
    public ResponseEntity<LedgerEntry> recordTransaction(@RequestBody Map<String, Object> payload) {
        String caseId = (String) payload.getOrDefault("case_id", "case_unknown");
        String action = (String) payload.getOrDefault("action", "recovery_action");
        double amount = 0.0;
        if (payload.containsKey("amount")) {
            Object amtObj = payload.get("amount");
            if (amtObj instanceof Number) {
                amount = ((Number) amtObj).doubleValue();
            }
        }
        String timestamp = (String) payload.getOrDefault("timestamp", "");

        LedgerEntry entry = ledgerService.recordTransaction(caseId, action, amount, timestamp);
        return ResponseEntity.ok(entry);
    }

    @GetMapping("/verify-chain")
    public ResponseEntity<Map<String, Object>> verifyChain() {
        Map<String, Object> result = ledgerService.verifyChain();
        return ResponseEntity.ok(result);
    }

    @PostMapping("/tamper-test")
    public ResponseEntity<Map<String, Object>> tamperRecord(
            @RequestParam(defaultValue = "1") long index,
            @RequestParam(defaultValue = "[MALICIOUS_TAMPER_ACTION]") String modifiedAction) {

        boolean tampered = ledgerService.tamperRecordForTesting(index, modifiedAction);
        if (tampered) {
            return ResponseEntity.ok(Map.of(
                    "message", "Record at index " + index + " was deliberately tampered with for security verification test.",
                    "modified_action", modifiedAction
            ));
        } else {
            return ResponseEntity.badRequest().body(Map.of(
                    "error", "Invalid index " + index + ". Ledger size: " + ledgerService.getAllEntries().size()
            ));
        }
    }

    @GetMapping("/records")
    public ResponseEntity<List<LedgerEntry>> getAllRecords() {
        return ResponseEntity.ok(ledgerService.getAllEntries());
    }
}
