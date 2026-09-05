package com.vaapsi.ledger;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@CrossOrigin(origins = "*")
public class RootController {

    private final LedgerService ledgerService;

    public RootController(LedgerService ledgerService) {
        this.ledgerService = ledgerService;
    }

    @GetMapping("/")
    public ResponseEntity<Map<String, Object>> root() {
        return ResponseEntity.ok(Map.of(
                "service", "Vaapsi (वापसी) Java Cryptographic Audit Ledger Microservice",
                "status", "running",
                "web_dashboard_url", "http://localhost:5173",
                "verify_chain_endpoint", "http://localhost:8088/api/ledger/verify-chain",
                "all_records_endpoint", "http://localhost:8088/api/ledger/records",
                "message", "Welcome to Vaapsi Audit Ledger. Open http://localhost:5173 to view the main web UI."
        ));
    }
}
