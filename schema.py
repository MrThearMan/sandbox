from typing import Literal, Optional, TypedDict, List, Union

__all__ = [
    "PullRequestEvent",
    "PullRequestCommentEvent",
]


AuthorAccociation = Literal[
    "COLLABORATOR",  # Author has been invited to collaborate on the repository.
    "CONTRIBUTOR",  # Author has previously committed to the repository.
    "FIRST_TIMER",  # Author has not previously committed to GitHub.
    "FIRST_TIME_CONTRIBUTOR",  # Author has not previously committed to the repository.
    "MANNEQUIN",  # Author is a placeholder for an unclaimed user.
    "MEMBER",  # Author is a member of the organization that owns the repository.
    "NONE",  # Author has no association with the repository.
    "OWNER",  # Author is the owner of the repository.
]

MergeableStateStatus = Literal[
    "behind",  # The head ref is out of date.
    "blocked",  # The merge is blocked.
    "clean",  # Mergeable and passing commit status.
    "dirty",  # The merge commit cannot be cleanly created.
    "draft",  # The merge is blocked due to the pull request being a draft.
    "has_hooks",  # Mergeable with passing commit status and pre-receive hooks.
    "unknown",  # The state cannot currently be determined.
    "unstable",  # Mergeable with non-passing commit status.
]


PullRequestEventAction = Literal[
    "assigned",  # A pull request was assigned to a user.
    "auto_merge_disabled",  # Auto merge was disabled for a pull request.
    "auto_merge_enabled",  # Auto merge was enabled for a pull request.
    "closed",  # A pull request was closed. Check payload `merged` value!
    "converted_to_draft",  # A pull request was converted to a draft.
    "demilestoned",  # A pull request was removed from a milestone.
    "dequeued",  # A pull request was removed from the merge queue.
    "edited",  # The title or body of a pull request was edited, or the base branch of a pull request was changed.
    "enqueued",  # A pull request was added to the merge queue.
    "labeled",  # A label was added to a pull request.
    "locked",  # Conversation on a pull request was locked.
    "milestoned",  # A pull request was added to a milestone.
    "opened",  # A pull request was created.
    "ready_for_review",  # A draft pull request was marked as ready for review.
    "reopened",  # A previously closed pull request was reopened.
    "review_request_removed",  # A request for review by a person or team was removed from a pull request.
    "review_requested",  # Review by a person or team was requested for a pull request.
    "synchronize",  # A pull request's head branch was updated, e.g. new commits or new base branch.
    "unassigned",  # A user was unassigned from a pull request.
    "unlabeled",  # A label was removed from a pull request.
    "unlocked",  # Conversation on a pull request was unlocked.
]


class User(TypedDict):
    avatar_url: str
    """The URL to the avatar of the user."""

    events_url: str
    """The URL to the events of the user."""

    followers_url: str
    """The URL to the followers of the user."""

    following_url: str
    """The URL to the following of the user."""

    gists_url: str
    """The URL to the gists of the user."""

    gravatar_id: str
    """The Gravatar ID of the user."""

    html_url: str
    """The URL to the user."""

    id: int
    """The ID of the user."""

    login: str
    """The login of the user."""

    node_id: str
    """Global Node ID (GraphQL) for the user"""

    organizations_url: str
    """The URL to the organizations of the user."""

    received_events_url: str
    """The URL to the received events of the user."""

    repos_url: str
    """The URL to the repos of the user."""

    site_admin: bool
    """Whether the user is a site admin."""

    starred_url: str
    """The URL to the starred of the user."""

    subscriptions_url: str
    """The URL to the subscriptions of the user."""

    type: str
    """The type of the user."""

    url: str
    """The URL to the user."""


class Team(TypedDict):
    description: Optional[str]
    """The description of the team."""

    html_url: str
    """The URL to the team."""

    id: int
    """The ID of the team."""

    ldap_dn: str
    """The LDAP DN of the team."""

    members_url: str
    """The URL to the members of the team."""

    name: str
    """The name of the team."""

    node_id: str
    """Global Node ID (GraphQL) for the team"""

    notification_setting: str
    """The notification setting of the team."""

    permission: str
    """The permission of the team."""

    privacy: str
    """The privacy of the team."""

    repositories_url: str
    """The URL to the repositories of the team."""

    slug: str
    """The slug of the team."""

    url: str
    """The URL to the team."""


class Repository(TypedDict):
    allow_auto_merge: bool
    """Whether the repository allows auto-merge."""

    allow_forking: bool
    """Whether the repository allows forking."""

    allow_merge_commit: bool
    """Whether the repository allows merge commits."""

    allow_rebase_merge: bool
    """Whether the repository allows rebase merges."""

    allow_squash_merge: bool
    """Whether the repository allows squash merges."""

    allow_update_branch: bool
    """Whether the repository allows updating branches."""

    archive_url: str
    """The URL to the archive of the repository."""

    archived: bool
    """Whether the repository is archived."""

    assignees_url: str
    """The API URL to the assignees of the repository."""

    blobs_url: str
    """The API URL to the blobs of the repository."""

    branches_url: str
    """The API URL to the branches of the repository."""

    clone_url: str
    """The URL to the clone of the repository."""

    collaborators_url: str
    """The API URL to the collaborators of the repository."""

    comments_url: str
    """The API URL to the comments of the repository."""

    commits_url: str
    """The API URL to the commits of the repository."""

    compare_url: str
    """The API URL to the compare of the repository."""

    contents_url: str
    """The API URL to the contents of the repository."""

    contributors_url: str
    """The API URL to the contributors of the repository."""

    created_at: str  # datetime
    """The date and time the repository was created."""

    default_branch: str
    """The name of the default branch of the repository."""

    delete_branch_on_merge: str
    """Whether the repository deletes the branch on merge."""

    deployments_url: str
    """The API URL to the deployments of the repository."""

    description: str
    """The description of the repository."""

    disabled: bool
    """Whether the repository is disabled."""

    downloads_url: str
    """The API URL to the downloads of the repository."""

    events_url: str
    """The API URL to the events of the repository."""

    fork: bool
    """Whether the repository is a fork."""

    forks: int
    """The number of forks of the repository."""

    forks_count: int
    """The number of forks of the repository."""

    forks_url: str
    """The API URL to the forks of the repository."""

    full_name: str
    """The full name of the repository, e.g. '<org>/<repo>'."""

    git_commits_url: str
    """The API URL to the commits of the repository."""

    git_refs_url: str
    """The API URL to the refs of the repository."""

    git_tags_url: str
    """The API URL to the tags of the repository."""

    git_url: str
    """The GIT URL to the git of the repository."""

    has_discussions: bool
    """Whether the repository has discussions enabled."""

    has_downloads: bool
    """Whether the repository has downloads enabled."""

    has_issues: bool
    """Whether the repository has issues enabled."""

    has_pages: bool
    """Whether the repository has pages enabled."""

    has_projects: bool
    """Whether the repository has projects enabled."""

    has_wiki: bool
    """Whether the repository has the wiki enabled."""

    homepage: Optional[str]
    """The homepage of the repository."""

    hooks_url: str
    """The API URL to the hooks of the repository."""

    html_url: str
    """The URL to the repository."""

    id: int
    """The ID of the repository."""

    is_template: bool
    """Whether the repository is a template."""

    issue_comment_url: str
    """The API URL to the issue comments of the repository."""

    issue_events_url: str
    """The API URL to the issue events of the repository."""

    issues_url: str
    """The API URL to the issues of the repository."""

    keys_url: str
    """The API URL to the keys of the repository."""

    labels_url: str
    """The API URL to the labels of the repository."""

    language: str
    """The main programming language of the repository."""

    languages_url: str
    """The API URL to the languages of the repository."""

    license: Optional[str]
    """The license of the repository."""

    merge_commit_message: Literal["PR_BODY", "PR_TITLE", "BLANK"]
    """The merge commit message of the repository."""

    merge_commit_title: Literal["PR_TITLE", "MERGE_MESSAGE"]
    """The merge commit title of the repository. Only available from REF."""

    merges_url: str
    """The API URL to the merges of the repository."""

    milestones_url: str
    """The API URL to the milestones of the repository."""

    mirror_url: Optional[str]
    """The mirror URL of the repository."""

    name: str
    """The name of the repository."""

    node_id: str
    """Global Node ID (GraphQL) for the repository"""

    notifications_url: str
    """The API URL to the notifications of the repository."""

    open_issues: int
    """The number of open issues of the repository."""

    open_issues_count: int
    """The number of open issues of the repository."""

    owner: User
    """The owner of the repository."""

    private: bool
    """Whether the repository is private."""

    pulls_url: str
    """The API URL to the pulls of the repository."""

    pushed_at: str  # datetime
    """The date and time the repository was pushed."""

    releases_url: str
    """The API URL to the releases of the repository."""

    size: int
    """The size of the repository."""

    squash_merge_commit_message: Literal["PR_BODY", "COMMIT_MESSAGES", "BLANK"]
    """The squash merge commit message of the repository."""

    squash_merge_commit_title: Literal["PR_TITLE", "COMMIT_OR_PR_TITLE"]
    """The squash merge commit title of the repository."""

    ssh_url: str
    """The SSH URL of the repository."""

    stargazers_count: int
    """The number of stargazers of the repository."""

    stargazers_url: str
    """The API URL to the stargazers of the repository."""

    statuses_url: str
    """The API URL to the statuses of the repository."""

    subscribers_url: str
    """The API URL to the subscribers of the repository."""

    subscription_url: str
    """The API URL to the subscription of the repository."""

    svn_url: str
    """The SVN URL of the repository."""

    tags_url: str
    """The API URL to the tags of the repository."""

    teams_url: str
    """The API URL to the teams of the repository."""

    topics: List[str]
    """The topics of the repository."""

    trees_url: str
    """The API URL to the git trees of the repository."""

    updated_at: str  # datetime
    """The date and time the repository was last updated."""

    url: str
    """The URL to the repository."""

    use_squash_pr_title_as_default: str
    """Whether the squash merge commit title is the default."""

    visibility: Literal["public", "private", "internal"]
    """The visibility of the repository."""

    watchers: int
    """The number of watchers of the repository."""

    watchers_count: int
    """The number of watchers of the repository."""

    web_commit_signoff_required: bool
    """Whether the repository requires web commit signoff."""


class Ref(TypedDict):
    label: str
    """The label of the ref, e.g. '<org>/<branch>'"""

    ref: str
    """The ref the commit points to, e.g. '<branch>'."""

    repo: Repository
    """The repository the commit belongs to."""

    sha: str
    """The long SHA of the commit."""

    user: User
    """The user who created the commit."""


class AutoMergeStatus(TypedDict):
    enabled_by: User
    """GitHub user who enabled the auto-merge."""

    merge_method: Literal["merge", "rebase", "squash"]
    """The merge method to use."""

    commit_title: str
    """Title for the merge commit message."""

    commit_message: str
    """Commit message for the merge commit."""


class Milestone(TypedDict):
    closed_at: Optional[str]  # datetime
    """The date and time the milestone was closed"""

    closed_issues: int
    """The number of closed issues in the milestone"""

    created_at: str  # datetime
    """The date and time the milestone was created"""

    creator: User
    """The user who created the milestone"""

    description: str
    """The description of the milestone"""

    due_on: Optional[str]  # datetime
    """The date and time the milestone is due"""

    html_url: str
    """The URL to the milestone"""

    id: int
    """The ID of the milestone"""

    labels_url: str
    """The API URL to the labels on the milestone"""

    node_id: str
    """Global Node ID (GraphQL) for the milestone"""

    number: int
    """The number of the milestone"""

    open_issues: int
    """The number of open issues in the milestone"""

    state: Literal["open", "closed"]
    """The state of the milestone"""

    title: str
    """The title of the milestone"""

    updated_at: str  # datetime
    """The date and time the milestone was last updated"""

    url: str
    """URL to the milestone"""


class Label(TypedDict):
    color: str
    """6-character hex code, without the leading #, identifying the color"""

    default: bool
    """Whether the label is a default label"""

    description: Optional[str]
    """The description of the label"""

    id: int
    """The ID of the label"""

    name: str
    """The name of the label"""

    node_id: str
    """Global Node ID (GraphQL) for the label"""

    url: str
    """The URL for the label"""


class Comment(TypedDict):
    author_association: AuthorAccociation
    """The author association of the comment."""

    body: str
    """The body of the comment."""

    created_at: str  # datetime
    """The date and time the comment was created."""

    html_url: str
    """The URL to the comment."""

    id: int
    """The ID of the comment."""

    issue_url: str
    """The API URL to the issue (or pull request) associated with the comment."""

    node_id: str
    """Global Node ID (GraphQL) for the comment"""

    updated_at: str  # datetime
    """The date and time the comment was last updated."""

    url: str
    """The URL to the comment."""

    user: User
    """The user who created the comment."""


class PullRequest(TypedDict):
    active_lock_reason: Optional[str]
    """The reason for the pull request being locked."""

    additions: int
    """The number of additions in the pull request."""

    assignee: Optional[User]
    """The user who is assigned to the pull request."""

    assignees: List[User]
    """The users who are assigned to the pull request."""

    author_association: AuthorAccociation
    """The author association of the pull request."""

    auto_merge: Optional[AutoMergeStatus]
    """The auto merge status of the pull request."""

    base: Ref
    """The base ref of the pull request."""

    body: Optional[str]
    """The body of the pull request."""

    changed_files: int
    """The number of changed files in the pull request."""

    closed_at: Optional[str]
    """The date and time the pull request was closed."""

    comments: int
    """The number of comments on the pull request."""

    comments_url: str
    """The API URL to the comments on the pull request."""

    commits: int
    """The number of commits in the pull request."""

    commits_url: str
    """The API URL to the commits on the pull request."""

    created_at: str  # datetime
    """The date and time the pull request was created."""

    deletions: int
    """The number of deletions in the pull request."""

    diff_url: str
    """The URL to the diff of the pull request."""

    draft: bool
    """Whether the pull request is a draft."""

    head: Ref
    """The head ref of the pull request."""

    html_url: str
    """The URL to the pull request."""

    id: int
    """The ID of this event."""

    issue_url: str
    """The API URL to the issue associated with the pull request."""

    labels: List[Label]
    """The labels associated with the pull request."""

    locked: bool
    """Whether the pull request is locked."""

    maintainer_can_modify: bool
    """Whether the maintainer can modify the pull request."""

    merge_commit_sha: Optional[str]
    """The SHA of the merge commit."""

    mergeable: Optional[bool]
    """Whether the pull request is mergeable."""

    mergeable_state: MergeableStateStatus
    """The mergeable state of the pull request."""

    merged: bool
    """Whether the pull request has been merged."""

    merged_at: Optional[str]  # datetime
    """The date and time the pull request was merged."""

    merged_by: Optional[User]
    """The user who merged the pull request."""

    milestone: Optional[Milestone]
    """The milestone associated with the pull request."""

    node_id: str
    """Global Node ID (GraphQL) for the pull request"""

    number: int
    """The number of the pull request."""

    patch_url: str
    """The URL to the patch of the pull request."""

    rebaseable: Optional[bool]
    """Whether the pull request is rebaseable."""

    requested_reviewers: List[User]
    """The users who have requested reviews on the pull request."""

    requested_teams: List[Team]
    """The teams who have requested reviews on the pull request."""

    review_comment_url: str
    """The API URL to the review comments on the pull request."""

    review_comments: int
    """The number of review comments on the pull request."""

    review_comments_url: str
    """The API URL to the review comments on the pull request."""

    state: Literal["open", "closed"]
    """The state of the pull request."""

    statuses_url: str
    """The API URL to the statuses on the pull request."""

    title: str
    """The title of the pull request."""

    updated_at: str  # datetime
    """The date and time the pull request was last updated."""

    url: str
    """The URL to the pull request."""

    user: User
    """The user who opened the pull request."""


class PullRequestEvent(TypedDict):
    """Payload for GitHub event that occurs for a pull request.

    ref: https://docs.github.com/en/webhooks/webhook-events-and-payloads?actionType=opened#pull_request
    """

    action: PullRequestEventAction
    """The action that was performed."""

    number: int
    """The pull request number."""

    pull_request: PullRequest
    """The pull request accociated with the event."""

    repository: Repository
    """The repository on GitHub where the event occurred. """

    sender: User
    """The GitHub user that triggered the event."""


class PullRequestCommentEvent(TypedDict):
    """Payload for GitHub event for a pull request comment.

    Note: GitHub considers every pull request an issue.

    ref: https://docs.github.com/en/webhooks/webhook-events-and-payloads#issue_comment
    """

    action: Literal["created", "edited", "deleted"]
    """The action that was performed."""

    comment: Comment
    """The pull request number."""

    issue: PullRequest
    """The pull request where the comment was made."""

    repository: Repository
    """The repository on GitHub where the event occurred. """

    sender: User
    """The GitHub user that triggered the event."""


Event = Union[PullRequestEvent, PullRequestCommentEvent]
