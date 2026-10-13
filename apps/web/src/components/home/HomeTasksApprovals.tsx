"use client";

import React, { useState } from "react";
import { CheckSquare, Plus, ShieldAlert } from "lucide-react";
import { usePersonalTasks } from "@/hooks/home/usePersonalTasks";
import { useApprovalRequests } from "@/hooks/home/useApprovalRequests";
import { Task, TaskStatusFilter } from "@/lib/tasks/types";
import { ApprovalItem, ApprovalStatusFilter } from "@/lib/approvals/types";
import { HomeWidgetSurface } from "./HomeWidgetSurface";
import { PersonalTaskList } from "./PersonalTaskList";
import { PendingApprovalList } from "./PendingApprovalList";
import { TaskEditorDialog } from "./TaskEditorDialog";
import { ApprovalReviewDialog } from "./ApprovalReviewDialog";

export function HomeTasksApprovals() {
  const [activeTab, setActiveTab] = useState<"tasks" | "approvals">("tasks");
  const [taskFilter, setTaskFilter] = useState<TaskStatusFilter>("OPEN");
  const [approvalFilter, setApprovalFilter] = useState<ApprovalStatusFilter>("PENDING");

  // Dialog states
  const [isTaskEditorOpen, setIsTaskEditorOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isApprovalReviewOpen, setIsApprovalReviewOpen] = useState(false);
  const [reviewingApproval, setReviewingApproval] = useState<ApprovalItem | null>(null);

  // Task Hooks
  const {
    tasks,
    counts: taskCounts,
    isLoading: tasksLoading,
    isLoadingMore: tasksLoadingMore,
    isError: tasksError,
    error: taskErrorObj,
    hasMore: tasksHasMore,
    isMutating: tasksMutating,
    refetch: refetchTasks,
    loadMore: loadMoreTasks,
    createTask,
    updateTask,
    completeTask,
    reopenTask,
    cancelTask,
  } = usePersonalTasks(taskFilter, 5);

  // Approval Hooks
  const {
    approvals,
    counts: approvalCounts,
    isLoading: approvalsLoading,
    isLoadingMore: approvalsLoadingMore,
    isError: approvalsError,
    error: approvalErrorObj,
    hasMore: approvalsHasMore,
    isDeciding: approvalsDeciding,
    refetch: refetchApprovals,
    loadMore: loadMoreApprovals,
    getDetail: getApprovalDetail,
    decideApproval,
  } = useApprovalRequests(approvalFilter, 5);

  const handleOpenCreateTask = () => {
    setEditingTask(null);
    setIsTaskEditorOpen(true);
  };

  const handleOpenEditTask = (task: Task) => {
    setEditingTask(task);
    setIsTaskEditorOpen(true);
  };

  const handleOpenReviewApproval = (approval: ApprovalItem) => {
    setReviewingApproval(approval);
    setIsApprovalReviewOpen(true);
  };

  const openTaskCount = taskCounts?.open_count ?? 0;
  const pendingApprovalCount = approvalCounts?.pending_count ?? 0;

  return (
    <>
      <HomeWidgetSurface
        id="home-tasks-approvals"
        title="Tasks & Approvals"
        subtitle="Work to complete and decisions requiring your attention."
        actions={
          <div className="flex items-center gap-1.5">
            {activeTab === "tasks" && (
              <button
                type="button"
                onClick={handleOpenCreateTask}
                className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-medium text-atlas-teal hover:bg-atlas-teal/10 rounded transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-atlas-teal"
                aria-label="Add a new personal task"
              >
                <Plus className="h-3 w-3" aria-hidden="true" />
                <span>Add Task</span>
              </button>
            )}
          </div>
        }
      >
        <div className="flex flex-col gap-3">
          {/* Top Domain Switcher: My Tasks vs Pending Approvals */}
          <div className="flex items-center border-b border-atlas-border-subtle gap-4" role="tablist">
            <button
              type="button"
              role="tab"
              aria-selected={activeTab === "tasks"}
              onClick={() => setActiveTab("tasks")}
              className={`flex items-center gap-2 pb-2 text-xs font-semibold border-b-2 transition-colors ${
                activeTab === "tasks"
                  ? "border-atlas-teal text-atlas-text-primary"
                  : "border-transparent text-atlas-text-muted hover:text-atlas-text-secondary"
              }`}
            >
              <CheckSquare className="h-3.5 w-3.5" aria-hidden="true" />
              <span>My Tasks</span>
              <span
                className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
                  openTaskCount > 0
                    ? "bg-atlas-teal/20 text-atlas-teal font-semibold"
                    : "bg-atlas-surface-3 text-atlas-text-muted"
                }`}
              >
                {openTaskCount}
              </span>
            </button>

            <button
              type="button"
              role="tab"
              aria-selected={activeTab === "approvals"}
              onClick={() => setActiveTab("approvals")}
              className={`flex items-center gap-2 pb-2 text-xs font-semibold border-b-2 transition-colors ${
                activeTab === "approvals"
                  ? "border-amber-400 text-atlas-text-primary"
                  : "border-transparent text-atlas-text-muted hover:text-atlas-text-secondary"
              }`}
            >
              <ShieldAlert className="h-3.5 w-3.5" aria-hidden="true" />
              <span>Approvals</span>
              <span
                className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
                  pendingApprovalCount > 0
                    ? "bg-amber-500/20 text-amber-400 font-semibold"
                    : "bg-atlas-surface-3 text-atlas-text-muted"
                }`}
              >
                {pendingApprovalCount}
              </span>
            </button>
          </div>

          {/* Tab Content with Error Isolation */}
          {activeTab === "tasks" ? (
            <PersonalTaskList
              tasks={tasks}
              statusFilter={taskFilter}
              onFilterChange={setTaskFilter}
              isLoading={tasksLoading}
              isLoadingMore={tasksLoadingMore}
              isError={tasksError}
              error={taskErrorObj}
              hasMore={tasksHasMore}
              isMutating={tasksMutating}
              onRetry={refetchTasks}
              onLoadMore={loadMoreTasks}
              onOpenCreateDialog={handleOpenCreateTask}
              onComplete={completeTask}
              onReopen={reopenTask}
              onCancel={cancelTask}
              onEdit={handleOpenEditTask}
            />
          ) : (
            <PendingApprovalList
              approvals={approvals}
              statusFilter={approvalFilter}
              onFilterChange={setApprovalFilter}
              isLoading={approvalsLoading}
              isLoadingMore={approvalsLoadingMore}
              isError={approvalsError}
              error={approvalErrorObj}
              hasMore={approvalsHasMore}
              onRetry={refetchApprovals}
              onLoadMore={loadMoreApprovals}
              onReview={handleOpenReviewApproval}
            />
          )}
        </div>
      </HomeWidgetSurface>

      {/* Task Creation & Editing Dialog */}
      <TaskEditorDialog
        isOpen={isTaskEditorOpen}
        onClose={() => setIsTaskEditorOpen(false)}
        task={editingTask}
        onSubmitCreate={async (input) => {
          await createTask(input);
        }}
        onSubmitUpdate={async (taskId, input) => {
          await updateTask(taskId, input);
        }}
        isSubmitting={tasksMutating}
      />

      {/* Approval Review Dialog */}
      <ApprovalReviewDialog
        isOpen={isApprovalReviewOpen}
        onClose={() => setIsApprovalReviewOpen(false)}
        approvalItem={reviewingApproval}
        onFetchDetail={getApprovalDetail}
        onDecide={decideApproval}
        isDeciding={approvalsDeciding}
      />
    </>
  );
}
