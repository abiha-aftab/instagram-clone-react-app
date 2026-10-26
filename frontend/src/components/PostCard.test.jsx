import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { postAPI } from '../api';
import { makePost, me, renderWithAuth } from '../test/render';
import PostCard from './PostCard';

vi.mock('../api', async (importOriginal) => ({
  ...(await importOriginal()),
  postAPI: { like: vi.fn(), unlike: vi.fn(), remove: vi.fn(), comments: vi.fn() },
}));

describe('PostCard', () => {
  beforeEach(() => vi.resetAllMocks());

  it('offers Delete only on your own posts', () => {
    const { unmount } = renderWithAuth(<PostCard post={makePost()} onDeleted={() => {}} />);
    expect(screen.queryByRole('button', { name: 'Delete' })).not.toBeInTheDocument();
    unmount();

    renderWithAuth(<PostCard post={makePost({ author: { id: me.id, username: me.username } })} onDeleted={() => {}} />);
    expect(screen.getByRole('button', { name: 'Delete' })).toBeInTheDocument();
  });

  it('deletes after confirmation and reports the id', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    postAPI.remove.mockResolvedValue({});
    const onDeleted = vi.fn();
    renderWithAuth(<PostCard post={makePost({ author: { id: me.id, username: me.username } })} onDeleted={onDeleted} />);

    await userEvent.click(screen.getByRole('button', { name: 'Delete' }));
    expect(postAPI.remove).toHaveBeenCalledWith(10);
    expect(onDeleted).toHaveBeenCalledWith(10);
  });

  it('likes optimistically', async () => {
    postAPI.like.mockResolvedValue({});
    renderWithAuth(<PostCard post={makePost()} onDeleted={() => {}} />);

    await userEvent.click(screen.getByRole('button', { name: 'Like' }));
    expect(postAPI.like).toHaveBeenCalledWith(10);
    expect(screen.getByRole('button', { name: 'Liked' })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByText('4 likes')).toBeInTheDocument();
  });

  it('rolls the like back and explains when the API refuses', async () => {
    postAPI.like.mockRejectedValue({ response: { data: { detail: 'Not found.' } } });
    renderWithAuth(<PostCard post={makePost()} onDeleted={() => {}} />);

    await userEvent.click(screen.getByRole('button', { name: 'Like' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Not found.');
    expect(screen.getByText('3 likes')).toBeInTheDocument();
  });
});
