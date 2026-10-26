import { screen, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { postAPI } from '../api';
import { me, page, renderWithAuth } from '../test/render';
import CommentSection from './CommentSection';

vi.mock('../api', async (importOriginal) => ({
  ...(await importOriginal()),
  postAPI: { comments: vi.fn() },
  commentAPI: { create: vi.fn(), remove: vi.fn() },
}));

const comment = (id, user, username, replies = []) => ({
  id,
  user,
  username,
  text: `comment ${id}`,
  created_at: new Date().toISOString(),
  replies,
});

describe('CommentSection', () => {
  beforeEach(() => vi.resetAllMocks());

  it('shows Delete only on comments and replies you wrote', async () => {
    postAPI.comments.mockResolvedValue(
      page([comment(1, 2, 'teo', [comment(3, me.id, me.username)]), comment(2, me.id, me.username)]),
    );
    renderWithAuth(<CommentSection postId={10} />);

    const items = await screen.findAllByText(/^comment \d$/);
    const deleteButtons = items.map((item) =>
      within(item.closest('.comment')).queryByRole('button', { name: 'Delete' }),
    );
    expect(deleteButtons.map(Boolean)).toEqual([false, true, true]);
  });

  it('offers older comments when the API has another page', async () => {
    postAPI.comments
      .mockResolvedValueOnce(page([comment(1, 2, 'teo')], '/next'))
      .mockResolvedValueOnce(page([comment(2, 2, 'teo')]));
    renderWithAuth(<CommentSection postId={10} />);

    (await screen.findByRole('button', { name: 'Older comments' })).click();
    expect(await screen.findByText('comment 2')).toBeInTheDocument();
    expect(postAPI.comments).toHaveBeenLastCalledWith(10, 2);
  });
});
