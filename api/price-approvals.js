// Price Approvals API Endpoints
// Handles admin review and approval of flagged price changes

import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
);

export default async function handler(req, res) {
  // Only allow GET and POST requests
  if (!["GET", "POST"].includes(req.method)) {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const { action, id } = req.query;

    if (req.method === "GET") {
      // GET /api/price-approvals - List pending approvals
      return await handleGetApprovals(req, res);
    } else if (req.method === "POST") {
      // POST /api/price-approvals/:id/approve - Approve specific change
      // POST /api/price-approvals/:id/reject - Reject specific change
      // POST /api/price-approvals/bulk-approve - Bulk approve
      // POST /api/price-approvals/bulk-reject - Bulk reject

      if (action === "approve" && id) {
        return await handleApproveApproval(req, res, id);
      } else if (action === "reject" && id) {
        return await handleRejectApproval(req, res, id);
      } else if (action === "bulk-approve") {
        return await handleBulkApprove(req, res);
      } else if (action === "bulk-reject") {
        return await handleBulkReject(req, res);
      } else {
        return res.status(400).json({ error: "Invalid action specified" });
      }
    }
  } catch (error) {
    console.error("❌ Price approvals API error:", error);
    return res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString(),
    });
  }
}

// GET /api/price-approvals - List pending approvals
async function handleGetApprovals(req, res) {
  try {
    const { status = "pending", limit = 50, offset = 0 } = req.query;

    // Build query based on status
    let query = supabase
      .from("price_validation_queue")
      .select(
        `
        *,
        books_accessories (
          id,
          title,
          affiliate_link,
          price
        )
      `
      )
      .order("flagged_at", { ascending: false })
      .range(offset, offset + limit - 1);

    if (status !== "all") {
      query = query.eq("status", status);
    }

    const { data, error, count } = await query;

    if (error) throw error;

    // Get statistics
    const stats = await getApprovalStats();

    return res.status(200).json({
      success: true,
      data: data || [],
      statistics: stats,
      pagination: {
        limit: parseInt(limit),
        offset: parseInt(offset),
        total: count || 0,
      },
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("❌ Error fetching approvals:", error);
    return res.status(500).json({
      success: false,
      error: error.message,
    });
  }
}

// POST /api/price-approvals/:id/approve - Approve specific change
async function handleApproveApproval(req, res, id) {
  try {
    const { admin_notes } = req.body;
    const admin_id = req.headers["x-admin-id"] || "admin";

    // Get the approval record
    const { data: approval, error: fetchError } = await supabase
      .from("price_validation_queue")
      .select("*")
      .eq("id", id)
      .single();

    if (fetchError || !approval) {
      return res.status(404).json({
        success: false,
        error: "Approval not found",
      });
    }

    if (approval.status !== "pending") {
      return res.status(400).json({
        success: false,
        error: "Approval already processed",
      });
    }

    // Update the approval status
    const { error: updateError } = await supabase
      .from("price_validation_queue")
      .update({
        status: "approved",
        reviewed_at: new Date().toISOString(),
        reviewed_by: admin_id,
        admin_notes: admin_notes || null,
      })
      .eq("id", id);

    if (updateError) throw updateError;

    // Update the book price
    const { error: bookUpdateError } = await supabase
      .from("books_accessories")
      .update({
        price: approval.new_price,
        price_updated_at: new Date().toISOString(),
        last_validation_status: "approved",
        validation_notes: admin_notes || "Approved by admin",
        requires_approval: false,
      })
      .eq("id", approval.item_id);

    if (bookUpdateError) throw bookUpdateError;

    // Log to price history
    await logPriceHistory(
      approval.item_id,
      approval.old_price,
      approval.new_price,
      "approved",
      admin_notes
    );

    console.log(
      `✅ Price change APPROVED: Item ${approval.item_id}, ${approval.old_price} → ${approval.new_price}`
    );

    return res.status(200).json({
      success: true,
      message: "Price change approved successfully",
      data: {
        id: approval.id,
        item_id: approval.item_id,
        old_price: approval.old_price,
        new_price: approval.new_price,
        percentage_change: approval.percentage_change,
      },
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("❌ Error approving price change:", error);
    return res.status(500).json({
      success: false,
      error: error.message,
    });
  }
}

// POST /api/price-approvals/:id/reject - Reject specific change
async function handleRejectApproval(req, res, id) {
  try {
    const { admin_notes } = req.body;
    const admin_id = req.headers["x-admin-id"] || "admin";

    // Get the approval record
    const { data: approval, error: fetchError } = await supabase
      .from("price_validation_queue")
      .select("*")
      .eq("id", id)
      .single();

    if (fetchError || !approval) {
      return res.status(404).json({
        success: false,
        error: "Approval not found",
      });
    }

    if (approval.status !== "pending") {
      return res.status(400).json({
        success: false,
        error: "Approval already processed",
      });
    }

    // Update the approval status
    const { error: updateError } = await supabase
      .from("price_validation_queue")
      .update({
        status: "rejected",
        reviewed_at: new Date().toISOString(),
        reviewed_by: admin_id,
        admin_notes: admin_notes || null,
      })
      .eq("id", id);

    if (updateError) throw updateError;

    // Update the book validation status
    const { error: bookUpdateError } = await supabase
      .from("books_accessories")
      .update({
        last_validation_status: "rejected",
        validation_notes: admin_notes || "Rejected by admin",
        requires_approval: false,
      })
      .eq("id", approval.item_id);

    if (bookUpdateError) throw bookUpdateError;

    console.log(
      `❌ Price change REJECTED: Item ${approval.item_id}, ${approval.old_price} → ${approval.new_price}`
    );

    return res.status(200).json({
      success: true,
      message: "Price change rejected successfully",
      data: {
        id: approval.id,
        item_id: approval.item_id,
        old_price: approval.old_price,
        new_price: approval.new_price,
        percentage_change: approval.percentage_change,
      },
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("❌ Error rejecting price change:", error);
    return res.status(500).json({
      success: false,
      error: error.message,
    });
  }
}

// POST /api/price-approvals/bulk-approve - Bulk approve
async function handleBulkApprove(req, res) {
  try {
    const { ids, admin_notes } = req.body;
    const admin_id = req.headers["x-admin-id"] || "admin";

    if (!ids || !Array.isArray(ids) || ids.length === 0) {
      return res.status(400).json({
        success: false,
        error: "No approval IDs provided",
      });
    }

    // Get all pending approvals
    const { data: approvals, error: fetchError } = await supabase
      .from("price_validation_queue")
      .select("*")
      .in("id", ids)
      .eq("status", "pending");

    if (fetchError) throw fetchError;

    if (!approvals || approvals.length === 0) {
      return res.status(400).json({
        success: false,
        error: "No pending approvals found",
      });
    }

    // Update all approvals
    const { error: updateError } = await supabase
      .from("price_validation_queue")
      .update({
        status: "approved",
        reviewed_at: new Date().toISOString(),
        reviewed_by: admin_id,
        admin_notes: admin_notes || "Bulk approved by admin",
      })
      .in("id", ids)
      .eq("status", "pending");

    if (updateError) throw updateError;

    // Update book prices
    for (const approval of approvals) {
      await supabase
        .from("books_accessories")
        .update({
          price: approval.new_price,
          price_updated_at: new Date().toISOString(),
          last_validation_status: "approved",
          validation_notes: admin_notes || "Bulk approved by admin",
          requires_approval: false,
        })
        .eq("id", approval.item_id);

      // Log to price history
      await logPriceHistory(
        approval.item_id,
        approval.old_price,
        approval.new_price,
        "approved",
        admin_notes
      );
    }

    console.log(`✅ Bulk APPROVED ${approvals.length} price changes`);

    return res.status(200).json({
      success: true,
      message: `Bulk approved ${approvals.length} price changes`,
      data: {
        approved_count: approvals.length,
        approvals: approvals.map((a) => ({
          id: a.id,
          item_id: a.item_id,
          old_price: a.old_price,
          new_price: a.new_price,
        })),
      },
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("❌ Error bulk approving price changes:", error);
    return res.status(500).json({
      success: false,
      error: error.message,
    });
  }
}

// POST /api/price-approvals/bulk-reject - Bulk reject
async function handleBulkReject(req, res) {
  try {
    const { ids, admin_notes } = req.body;
    const admin_id = req.headers["x-admin-id"] || "admin";

    if (!ids || !Array.isArray(ids) || ids.length === 0) {
      return res.status(400).json({
        success: false,
        error: "No approval IDs provided",
      });
    }

    // Get all pending approvals
    const { data: approvals, error: fetchError } = await supabase
      .from("price_validation_queue")
      .select("*")
      .in("id", ids)
      .eq("status", "pending");

    if (fetchError) throw fetchError;

    if (!approvals || approvals.length === 0) {
      return res.status(400).json({
        success: false,
        error: "No pending approvals found",
      });
    }

    // Update all approvals
    const { error: updateError } = await supabase
      .from("price_validation_queue")
      .update({
        status: "rejected",
        reviewed_at: new Date().toISOString(),
        reviewed_by: admin_id,
        admin_notes: admin_notes || "Bulk rejected by admin",
      })
      .in("id", ids)
      .eq("status", "pending");

    if (updateError) throw updateError;

    // Update book validation status
    for (const approval of approvals) {
      await supabase
        .from("books_accessories")
        .update({
          last_validation_status: "rejected",
          validation_notes: admin_notes || "Bulk rejected by admin",
          requires_approval: false,
        })
        .eq("id", approval.item_id);
    }

    console.log(`❌ Bulk REJECTED ${approvals.length} price changes`);

    return res.status(200).json({
      success: true,
      message: `Bulk rejected ${approvals.length} price changes`,
      data: {
        rejected_count: approvals.length,
        approvals: approvals.map((a) => ({
          id: a.id,
          item_id: a.item_id,
          old_price: a.old_price,
          new_price: a.new_price,
        })),
      },
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("❌ Error bulk rejecting price changes:", error);
    return res.status(500).json({
      success: false,
      error: error.message,
    });
  }
}

// Helper function to get approval statistics
async function getApprovalStats() {
  try {
    const today = new Date().toISOString().split("T")[0];

    // Get pending count
    const { count: pendingCount } = await supabase
      .from("price_validation_queue")
      .select("*", { count: "exact", head: true })
      .eq("status", "pending");

    // Get approved today count
    const { count: approvedToday } = await supabase
      .from("price_validation_queue")
      .select("*", { count: "exact", head: true })
      .eq("status", "approved")
      .gte("reviewed_at", today);

    // Get rejected today count
    const { count: rejectedToday } = await supabase
      .from("price_validation_queue")
      .select("*", { count: "exact", head: true })
      .eq("status", "rejected")
      .gte("reviewed_at", today);

    return {
      pending: pendingCount || 0,
      approved_today: approvedToday || 0,
      rejected_today: rejectedToday || 0,
      total_flagged:
        (pendingCount || 0) + (approvedToday || 0) + (rejectedToday || 0),
    };
  } catch (error) {
    console.error("❌ Error getting approval stats:", error);
    return {
      pending: 0,
      approved_today: 0,
      rejected_today: 0,
      total_flagged: 0,
    };
  }
}

// Helper function to log price history
async function logPriceHistory(itemId, oldPrice, newPrice, action, notes) {
  try {
    const priceChange = newPrice - oldPrice;
    const priceChangePercent =
      oldPrice > 0 ? (priceChange / oldPrice) * 100 : null;

    await supabase.from("price_history").insert({
      book_id: itemId,
      old_price: oldPrice,
      new_price: newPrice,
      price_change: priceChange,
      price_change_percent: priceChangePercent,
      update_source: `admin_${action}`,
      notes: notes || `Price ${action} by admin`,
    });
  } catch (error) {
    console.error("❌ Error logging price history:", error);
  }
}

// Export configuration for Vercel
export const config = {
  maxDuration: 30, // 30 seconds max execution time
  regions: ["iad1"], // US East for better performance
};
