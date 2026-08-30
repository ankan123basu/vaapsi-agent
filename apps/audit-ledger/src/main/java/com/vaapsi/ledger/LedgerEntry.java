package com.vaapsi.ledger;

public class LedgerEntry {
    private long index;
    private String caseId;
    private String action;
    private double amount;
    private String timestamp;
    private String previousHash;
    private String currentHash;

    public LedgerEntry() {
    }

    public LedgerEntry(long index, String caseId, String action, double amount, String timestamp, String previousHash, String currentHash) {
        this.index = index;
        this.caseId = caseId;
        this.action = action;
        this.amount = amount;
        this.timestamp = timestamp;
        this.previousHash = previousHash;
        this.currentHash = currentHash;
    }

    public long getIndex() {
        return index;
    }

    public void setIndex(long index) {
        this.index = index;
    }

    public String getCaseId() {
        return caseId;
    }

    public void setCaseId(String caseId) {
        this.caseId = caseId;
    }

    public String getAction() {
        return action;
    }

    public void setAction(String action) {
        this.action = action;
    }

    public double getAmount() {
        return amount;
    }

    public void setAmount(double amount) {
        this.amount = amount;
    }

    public String getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(String timestamp) {
        this.timestamp = timestamp;
    }

    public String getPreviousHash() {
        return previousHash;
    }

    public void setPreviousHash(String previousHash) {
        this.previousHash = previousHash;
    }

    public String getCurrentHash() {
        return currentHash;
    }

    public void setCurrentHash(String currentHash) {
        this.currentHash = currentHash;
    }
}
